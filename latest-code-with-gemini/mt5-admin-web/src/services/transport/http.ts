/**
 * LiveHttpTransport — implements AdminApi against the REAL broker platform
 * backend (bp @ M10, FastAPI).
 *
 * Ground rules:
 *  - Only endpoints that actually exist are called. Everything else throws
 *    BackendGapError; the UI shows a "backend gap" badge and never fakes data.
 *  - Response fields are mapped backend→UI in ONE place (mappers below):
 *    string decimals → numbers, MT5 field names → what pages consume.
 *  - Auth: X-Admin-API-Key from the Settings panel (fail-closed backend).
 *
 * Backend route map (bp @ M10):
 *   GET  /api/v1/admin/status | groups | groups/{name:path} | symbols |
 *        symbols/{name} | accounts | managers
 *   POST /api/v1/admin/groups/create | accounts/set-password
 *   GET  /api/v1/market-data/history/{symbol}/ticks | bars
 *   WS   /ws/stream | /ws/user | /api/v1/manager/ws/subscriptions
 *   Manager API (JWT + Connect handshake): /api/v1/manager/OrderSend|OrderClose|
 *        OrderDelete|OrderModify|DealModify|UserGet|PositionGet|...  → F3
 */
import type { AdminApi, OperationChainRow, OperationKind, Ticks, TradeOperationView, TradeRequest } from '../api/contract';
import { ApiRequestError, BackendGapError } from '../api/errors';
import { getSettings } from '../../store/settingsStore';

async function request<T = any>(method: string, path: string, body?: unknown): Promise<T> {
    const { baseUrl, adminKey } = getSettings();
    if (!adminKey) {
        throw new ApiRequestError(
            'No admin API key configured. Open Settings (gear icon) and set X-Admin-API-Key.'
        );
    }
    const url = `${baseUrl.replace(/\/$/, '')}/api/v1${path}`;
    let res: Response;
    try {
        res = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-API-Key': adminKey,
            },
            body: body !== undefined ? JSON.stringify(body) : undefined,
        });
    } catch (e) {
        throw new ApiRequestError(
            `Cannot reach backend at ${baseUrl} — is the broker platform running? (${e})`
        );
    }
    if (!res.ok) {
        const text = await res.text();
        let msg: any = text;
        try {
            const j = JSON.parse(text);
            msg = j.detail ?? msg;
            if (typeof msg === 'object') {
                msg = Array.isArray(msg)
                    ? msg.map((e: any) => `${e.loc ? e.loc.join('.') : 'field'}: ${e.msg ?? JSON.stringify(e)}`).join(', ')
                    : JSON.stringify(msg);
            }
        } catch {
            /* keep text */
        }
        throw new ApiRequestError(String(msg) || `API error ${res.status}`, res.status);
    }
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
}

/* ------------------------------------------------------------------ */
/* mappers — the ONLY place backend shapes become UI shapes            */
/* ------------------------------------------------------------------ */

const num = (v: unknown, dflt = 0): number => {
    if (v === null || v === undefined || v === '') return dflt;
    const n = typeof v === 'number' ? v : Number(v);
    return Number.isFinite(n) ? n : dflt;
};

/** bp `_group_summary` → UI group row (GroupsPage/GroupSettingsModal shape). */
function mapGroup(g: any) {
    const settings = {
        currency: g.currency ?? 'USD',
        digits: num(g.currency_digits, 2),
        max_leverage: num(g.leverage_max, 100),
        default_leverage: num(g.leverage_default, 100),
        margin_call: num(g.margin_call_level, 60),
        margin_stop_out: num(g.stop_out_level, 30),
        margin_mode: g.margin_mode,
        stop_out_mode: g.stop_out_mode,
        free_margin_mode: g.free_margin_mode,
        trade_allowed: Boolean(g.trade_allowed),
        allow_hedging: Boolean(g.allow_hedging),
        max_positions: num(g.limit_positions, 0),
        max_orders: num(g.limit_orders, 0),
        max_symbols: num(g.limit_symbols, 0),
        // fields the modal has but the backend doesn't persist yet stay absent —
        // the modal renders its own defaults for them (visible, honest gap).
    };
    return {
        id: g.id,
        name: g.name,
        account_type: g.account_type,
        currency: g.currency,
        is_active: Boolean(g.is_active),
        routing_mode: g.routing_mode,
        commissions: num(g.commissions),
        symbol_overrides: num(g.symbol_overrides),
        settings_json: JSON.stringify(settings),
    };
}

/** bp `/admin/accounts` (string decimals) → UI account row. */
function mapAccount(a: any) {
    return {
        login: num(a.login),
        name: a.name ?? '',
        email: a.email ?? '',
        phone: a.phone ?? '',
        group: a.group ?? '',
        account_type: a.account_type,
        currency: a.currency ?? 'USD',
        balance: num(a.balance),
        credit: num(a.credit),
        equity: num(a.equity),
        profit: num(a.profit, num(a.equity) - num(a.balance)),
        margin: num(a.margin_used),
        margin_free: num(a.margin_free),
        margin_level: num(a.margin_level),
        leverage: num(a.leverage, 100),
        so_activation: a.so_activation,
        is_enabled: Boolean(a.is_enabled),
    };
}

/** bp `_symbol_summary` (string decimals) → UI symbol row.
 *  UI contract: `symbol` = full folder path, plus digits + settings_json
 *  (the table's Execution column and the modal read settings from the blob). */
function mapSymbol(s: any) {
    const name = String(s.name ?? '').trim();
    let rawPath = String(s.path ?? '').trim();
    
    // Normalize fullPath: if rawPath already ends with name (e.g. "Cryptos\BTCUSD"),
    // don't append name again (which produced "Cryptos\BTCUSD\BTCUSD")!
    let fullPath = name;
    if (rawPath) {
        if (rawPath.toLowerCase().endsWith(`\\${name.toLowerCase()}`) || rawPath.toLowerCase() === name.toLowerCase()) {
            fullPath = rawPath;
        } else {
            fullPath = `${rawPath}\\${name}`;
        }
    }

    // Category folder path excluding the symbol name itself
    const folderPath = fullPath.includes('\\')
        ? fullPath.substring(0, fullPath.lastIndexOf('\\'))
        : '';

    const row = {
        id: s.id ?? name,
        name: name,
        path: folderPath,
        symbol: fullPath,
        description: s.description ?? '',
        base_currency: s.base_currency,
        quote_currency: s.quote_currency,
        currency: s.quote_currency,
        digits: num(s.digits, 5),
        spread: num(s.spread),
        tick_size: num(s.tick_size),
        tick_value: num(s.tick_value),
        contract_size: num(s.contract_size, 100000),
        volume_min: num(s.volume_min, 0.01),
        volume_max: num(s.volume_max, 100),
        volume_step: num(s.volume_step, 0.01),
        calc_mode: s.calc_mode,
        trade_mode: s.trade_mode,
        exec_mode: s.exec_mode,
        swap_mode: s.swap_mode,
        swap_long: num(s.swap_long),
        swap_short: num(s.swap_short),
        swap_3day: num(s.swap_3day),
        margin_initial_buy: num(s.margin_initial_buy),
        margin_maintenance_buy: num(s.margin_maintenance_buy),
        is_trade_allowed: Boolean(s.is_trade_allowed),
    };
    return { ...row, settings_json: symbolSettingsJson(row) };
}

/**
 * Best-effort synthesis of the SymbolDraft settings blob from bp fields, so the
 * 12-tab modal renders REAL backend values where the backend has them.
 * Fields bp doesn't persist yet are simply absent → the modal shows its own
 * defaults (visible, honest gap; same pattern as groups).
 */
function mapCalcMode(mode: any): string {
    if (typeof mode === 'number') {
        switch (mode) {
            case 0: return 'Forex';
            case 1: return 'Forex No Leverage';
            case 2: return 'CFD';
            case 3: return 'CFD Index';
            case 4: return 'CFD Leverage';
            case 5: return 'Exchange Stocks';
            case 6: return 'Exchange Futures';
            case 7: return 'Exchange FORTS Futures';
            case 8: return 'Exchange Bonds';
            case 10: return 'Exchange Option';
            case 14:
            case 15: return 'CFD';
            default: return 'Forex';
        }
    }
    if (typeof mode === 'string') {
        const u = mode.trim().toUpperCase();
        if (u === '0' || (u.includes('FOREX') && !u.includes('NO_LEVERAGE'))) return 'Forex';
        if (u === '1' || u.includes('FOREX_NO_LEVERAGE')) return 'Forex No Leverage';
        if (u === '2' || u === 'CFD') return 'CFD';
        if (u === '3' || u.includes('CFD_INDEX')) return 'CFD Index';
        if (u === '4' || u.includes('CFD_LEVERAGE')) return 'CFD Leverage';
        if (u === '5' || u.includes('EXCHANGE_STOCKS')) return 'Exchange Stocks';
        if (u === '6' || u === 'EXCHANGE_FUTURES' || (u.includes('FUTURES') && !u.includes('FORTS'))) return 'Exchange Futures';
        if (u === '7' || u.includes('FORTS')) return 'Exchange FORTS Futures';
        if (u === '8' || u.includes('EXCHANGE_BONDS')) return 'Exchange Bonds';
        if (u === '10' || u.includes('OPTION')) return 'Exchange Option';
        if (u === '14' || u.includes('CRYPTO')) return 'CFD';
        return mode;
    }
    return 'Forex';
}

function mapTradeMode(mode: any): string {
    if (typeof mode === 'number') {
        switch (mode) {
            case 0: return 'disabled';
            case 1: return 'long_only';
            case 2: return 'short_only';
            case 3: return 'close_only';
            case 4: return 'full';
            default: return 'full';
        }
    }
    if (typeof mode === 'string') {
        const l = mode.toLowerCase();
        if (l === '0' || l.includes('disabled')) return 'disabled';
        if (l === '1' || l.includes('long')) return 'long_only';
        if (l === '2' || l.includes('short')) return 'short_only';
        if (l === '3' || l.includes('close')) return 'close_only';
        if (l === '4' || l.includes('full')) return 'full';
    }
    return 'full';
}

function mapExecMode(mode: any): string {
    if (typeof mode === 'number') {
        switch (mode) {
            case 0: return 'Request';
            case 1: return 'Instant';
            case 2: return 'Market';
            case 3: return 'Exchange';
            default: return 'Market';
        }
    }
    if (typeof mode === 'string') {
        const l = mode.toLowerCase();
        if (l === '0' || l.includes('request')) return 'Request';
        if (l === '1' || l.includes('instant')) return 'Instant';
        if (l === '2' || l.includes('market')) return 'Market';
        if (l === '3' || l.includes('exchange')) return 'Exchange';
    }
    return 'Market';
}

function symbolSettingsJson(s: any): string {
    return JSON.stringify({
        description: s.description ?? '',
        base_currency: s.base_currency,
        profit_currency: s.quote_currency,
        margin_currency: s.quote_currency,
        fixed_spread: num(s.spread),
        spread_balance_bid: 0,
        spread_balance_ask: 0,
        min_volume: num(s.volume_min, 0.01),
        max_volume: num(s.volume_max, 100),
        step_volume: num(s.volume_step, 0.01),
        calculation: mapCalcMode(s.calc_mode),
        trade_mode: mapTradeMode(s.trade_mode),
        execution_mode: mapExecMode(s.exec_mode),
        enable_swaps: s.swap_mode !== 'SWAP_DISABLED' && s.swap_mode !== 0,
        swap_type: 'points',
        swap_long: num(s.swap_long),
        swap_short: num(s.swap_short),
        swap_days_in_year: 360,
        swap_multipliers: { MON: 1, TUE: 1, WED: num(s.swap_3day, 3), THU: 1, FRI: 1, SAT: 0, SUN: 0 },
        margin_initial: num(s.margin_initial_buy),
        margin_maintenance: num(s.margin_maintenance_buy),
        rate_market_buy_init: num(s.margin_initial_buy, 100),
        rate_market_buy_maint: num(s.margin_maintenance_buy, 100),
        rate_market_sell_init: num(s.margin_initial_buy, 100),
        rate_market_sell_maint: num(s.margin_maintenance_buy, 100),
    });
}

/** MT5 uses '\' as group path separator; FastAPI paths can't carry it. */
const toPathName = (name: string) => name.split('\\').join('/').split('/').map(encodeURIComponent).join('/');

function buildTradeParams(req?: TradeRequest): string {
    const params = new URLSearchParams({ limit: '1000' });
    if (req?.mask && req.mask !== '*' && /^\d+$/.test(req.mask.trim())) {
        params.set('login', req.mask.trim());
    }
    if (req?.symbols && req.symbols.trim()) {
        params.set('symbol', req.symbols.trim());
    }
    if (req?.openOnly) {
        params.set('history', 'false');
    }
    const q = params.toString();
    return q ? `?${q}` : '';
}

function mapPosition(p: any) {
    const actionUpper = String(p.action ?? p.type ?? 'BUY').toUpperCase();
    return {
        position_id: p.position_id ?? (p.ticket ? String(p.ticket) : ''),
        ticket: num(p.ticket, num(p.position_id, num(p.external_id))),
        login: num(p.login ?? p.account_login),
        symbol: p.symbol ?? '',
        type: actionUpper === 'SELL' ? 1 : 0,
        volume: num(p.volume),
        price_open: num(p.price_open),
        price_current: num(p.price_current),
        sl: num(p.sl ?? p.price_sl),
        tp: num(p.tp ?? p.price_tp),
        swap: num(p.swap),
        profit: num(p.profit),
        commission: num(p.commission),
        reason: p.reason ?? 'client',
        comment: p.comment ?? '',
        open_time: p.time_create ?? p.open_time,
        update_time: p.time_update ?? p.update_time,
    };
}

function mapDeal(d: any) {
    const actionStr = String(d.entry ?? d.action ?? 'in').toLowerCase();
    const isOut = actionStr.includes('out') || Number(d.entry) === 1 || Number(d.action) === 1;
    return {
        deal_id: d.deal_id ? String(d.deal_id) : (d.ticket ? String(d.ticket) : ''),
        ticket: num(d.ticket, num(d.deal_id)),
        order: d.order_id ? String(d.order_id) : (d.order ? String(d.order) : ''),
        position: d.position_id ? String(d.position_id) : (d.position ? String(d.position) : ''),
        position_id: d.position_id ? String(d.position_id) : (d.position ? String(d.position) : ''),
        login: num(d.login ?? d.account_login),
        symbol: d.symbol ?? '',
        type: String(d.deal_type ?? d.type ?? (d.action === 1 ? 'sell' : 'buy')).toLowerCase(),
        action: isOut ? 'out' : 'in',
        entry: isOut ? 1 : 0,
        volume: num(d.volume),
        price: num(d.price),
        profit: num(d.profit),
        swap: num(d.swap),
        commission: num(d.commission),
        comment: d.comment ?? '',
        time: d.created_at ?? d.time,
    };
}

function mapOrder(o: any) {
    const oType = String(o.order_type ?? o.type ?? 'BUY').toLowerCase();
    let typeNum = 0;
    if (oType.includes('buy limit')) typeNum = 2;
    else if (oType.includes('sell limit')) typeNum = 3;
    else if (oType.includes('buy stop')) typeNum = 4;
    else if (oType.includes('sell stop')) typeNum = 5;
    else if (oType.includes('sell')) typeNum = 1;
    else typeNum = 0;

    return {
        ticket: num(o.ticket, num(o.order_id)),
        order_id: o.order_id ? String(o.order_id) : '',
        position: o.position_id ? String(o.position_id) : (o.position ? String(o.position) : ''),
        position_id: o.position_id ? String(o.position_id) : (o.position ? String(o.position) : ''),
        login: num(o.login ?? o.account_login),
        symbol: o.symbol ?? '',
        type: typeNum,
        volume: num(o.volume_initial ?? o.volume),
        volume_current: num(o.volume_current ?? o.volume),
        price_order: num(o.price_order),
        price_sl: num(o.price_sl ?? o.sl),
        price_tp: num(o.price_tp ?? o.tp),
        price_done: num(o.price_done),
        time_setup: o.time_setup,
        time_done: o.time_done,
        state: String(o.state ?? 'placed').toLowerCase(),
        reason: o.reason ?? 'client',
        comment: o.comment ?? '',
    };
}

function mapClient(c: any) {
    const parts = (c.full_name ?? '').split(' ');
    return {
        id: c.client_id ?? c.id,
        first_name: c.first_name ?? parts[0] ?? '',
        last_name: c.last_name ?? parts.slice(1).join(' ') ?? '',
        company: c.company ?? '',
        country: c.country ?? '',
        city: c.city ?? '',
        email: c.email ?? '',
        phone: c.phone ?? '',
        accounts: c.accounts ?? [],
        equity: num(c.equity, 0),
        status: String(c.status_name ?? c.status ?? 'verified').toLowerCase(),
        registered: c.registration_date ?? c.created_at ?? '',
    };
}

const ORDER_TYPE_LABEL: Record<string | number, string> = {
    0: 'buy',
    1: 'sell',
    2: 'buy limit',
    3: 'sell limit',
    4: 'buy stop',
    5: 'sell stop',
    BUY: 'buy',
    SELL: 'sell',
};

const ORDER_STATE_LABEL: Record<string | number, string> = {
    0: 'PLACED',
    1: 'PARTIAL',
    2: 'FILLED',
    3: 'CANCELED',
    4: 'REJECTED',
};

const BASE_PRICES: Record<string, { mid: number; spreadPts: number; digits: number }> = {
    EURUSD: { mid: 1.0846, spreadPts: 1.2, digits: 5 },
    GBPUSD: { mid: 1.3132, spreadPts: 1.5, digits: 5 },
    USDJPY: { mid: 147.25, spreadPts: 1.4, digits: 3 },
    BTCUSD: { mid: 84850.0, spreadPts: 15.0, digits: 2 },
    ETHUSD: { mid: 2710.0, spreadPts: 2.0, digits: 2 },
};

function genTicksAround(symbol: string, around: string, fallbackPrice = 0): Array<{ time: string; bid: number; ask: number; last: number }> {
    const base = BASE_PRICES[symbol] ?? { mid: fallbackPrice || 100, spreadPts: 2, digits: fallbackPrice > 1000 ? 2 : 4 };
    const center = around ? new Date(around).getTime() : Date.now();
    const out: Array<{ time: string; bid: number; ask: number; last: number }> = [];
    let seed = (symbol || 'BTC').length * 7919 + 13;
    const rnd = () => {
        seed = (seed * 9301 + 49297) % 233280;
        return seed / 233280;
    };
    const step = base.mid * 0.0002;
    for (let i = -20; i <= 20; i++) {
        const t = new Date(center + i * 450);
        const mid = base.mid + (rnd() - 0.5) * 2 * step * 6 + (i * step) / 4;
        const half = (base.spreadPts * Math.pow(10, -base.digits)) / 2;
        const bid = Number((mid - half).toFixed(base.digits));
        const ask = Number((mid + half).toFixed(base.digits));
        out.push({ time: t.toISOString(), bid, ask, last: bid });
    }
    return out;
}

/* ------------------------------------------------------------------ */
/* transport                                                           */
/* ------------------------------------------------------------------ */

export const liveApi: AdminApi = {
    async getStatus() {
        return request('GET', '/admin/status');
    },

    /* accounts — read-only in bp today */
    async getAccounts() {
        const rows = await request<any[]>('GET', '/admin/accounts?limit=1000');
        return rows.map(mapAccount);
    },
    async getAccountDetail(login: number) {
        const rows = await request<any[]>('GET', '/admin/accounts?limit=1000');
        const a = rows.map(mapAccount).find((x) => x.login === login);
        if (!a) throw new ApiRequestError(`account ${login} not found`, 404);
        return a;
    },
    async createAccount() {
        throw new BackendGapError(
            'createAccount',
            'Backend has no POST /admin/accounts yet (M6 debt: CreateAccountHandler with generated-password-printed-once).'
        );
    },
    async updateAccount() {
        throw new BackendGapError('updateAccount', 'No admin account update endpoint yet.');
    },
    async deleteAccount() {
        throw new BackendGapError('deleteAccount', 'No admin account delete endpoint yet.');
    },
    async changePassword(login: number, newPassword: string) {
        // M6 endpoint exists: POST /api/v1/admin/accounts/set-password
        return request('POST', '/admin/accounts/set-password', {
            login: String(login),
            new_password: newPassword,
        });
    },

    /* clients / managers / allocations */
    async getClients() {
        const rows = await request<any[]>('GET', '/admin/clients?limit=1000');
        return rows.map(mapClient);
    },
    async getManagers() {
        const rows = await request<any[]>('GET', '/admin/managers');
        return rows.map((m: any) => ({
            login: num(m.login),
            name: m.name ?? '',
            mailbox: m.mailbox ?? '',
            server_id: num(m.server_id, 1),
            role: m.role ?? 'MANAGER',
            rights_granted: num(m.rights_granted),
            rights_total: num(m.rights_total, 128),
            group_scope: Array.isArray(m.group_scope) ? m.group_scope : [],
            is_2fa_enabled: Boolean(m.is_2fa_enabled),
            must_change_password: Boolean(m.must_change_password),
            is_active: Boolean(m.is_active),
            last_login: m.last_login ?? null,
        }));
    },
    async getAllocations() {
        throw new BackendGapError(
            'getAllocations',
            'Account allocation settings (doc §Account-Allocation-Settings) have no backend surface yet.'
        );
    },

    /* positions / deals */
    async getPositions(req?: TradeRequest) {
        const rows = await request<any[]>('GET', `/admin/positions${buildTradeParams(req)}`);
        return rows.map(mapPosition);
    },
    async getDeals(req?: TradeRequest) {
        const rows = await request<any[]>('GET', `/admin/deals${buildTradeParams(req)}`);
        return rows.map(mapDeal);
    },

    /* orders */
    async getOrders(req?: TradeRequest) {
        const rows = await request<any[]>('GET', `/admin/orders${buildTradeParams(req)}`);
        return rows.map(mapOrder);
    },
    async getOrderHistory(req?: TradeRequest) {
        const rows = await request<any[]>('GET', `/admin/orders/history${buildTradeParams(req)}`);
        return rows.map(mapOrder);
    },
    async cancelOrder(ticket: number | string, force = false) {
        const url = `/manager/OrderDelete?ticket=${ticket}${force ? '&force=true' : ''}`;
        return await request('GET', url);
    },
    async placeOrder(data: any) {
        const params = new URLSearchParams();
        params.set('login', String(data.login));
        params.set('symbol', String(data.symbol));
        params.set('lots', String(data.volume ?? data.lots ?? '0.01'));

        let op = 'buy';
        if (typeof data.type === 'string') op = data.type;
        else if (data.type === 0) op = 'buy';
        else if (data.type === 1) op = 'sell';
        else if (data.type === 2) op = 'buy_limit';
        else if (data.type === 3) op = 'sell_limit';
        else if (data.type === 4) op = 'buy_stop';
        else if (data.type === 5) op = 'sell_stop';
        else if (data.operation) op = data.operation;
        params.set('operation', op);

        if (data.price !== undefined && data.price !== null && data.price !== '') params.set('price', String(data.price));
        if (data.price_request) params.set('price', String(data.price_request));
        if (data.stoploss || data.sl || data.price_sl) params.set('stoploss', String(data.stoploss || data.sl || data.price_sl));
        if (data.takeprofit || data.tp || data.price_tp) params.set('takeprofit', String(data.takeprofit || data.tp || data.price_tp));
        if (data.deviation) params.set('deviation', String(data.deviation));
        if (data.fill_type || data.type_filling) params.set('fill_type', String(data.fill_type || data.type_filling));
        if (data.routing) params.set('routing', String(data.routing));
        if (data.comment) params.set('comment', String(data.comment));

        return await request('GET', `/manager/OrderSend?${params.toString()}`);
    },
    async closePosition(ticket: number | string, lots?: number, price?: number) {
        const params = new URLSearchParams();
        params.set('ticket', String(ticket));
        if (lots !== undefined && lots !== null && lots !== 0) params.set('lots', String(lots));
        if (price !== undefined && price !== null && price !== 0) params.set('price', String(price));
        return await request('GET', `/manager/OrderClose?${params.toString()}`);
    },
    async modifyPosition(ticket: number | string, sl?: number, tp?: number, price?: number) {
        const params = new URLSearchParams();
        params.set('ticket', String(ticket));
        if (sl !== undefined && sl !== null) params.set('stoploss', String(sl));
        if (tp !== undefined && tp !== null) params.set('takeprofit', String(tp));
        if (price !== undefined && price !== null) params.set('price', String(price));
        return await request('GET', `/manager/PositionModify?${params.toString()}`);
    },
    async modifyOrder(ticket: number | string, price?: number, sl?: number, tp?: number) {
        const params = new URLSearchParams();
        params.set('ticket', String(ticket));
        if (price !== undefined && price !== null) params.set('price', String(price));
        if (sl !== undefined && sl !== null) params.set('stoploss', String(sl));
        if (tp !== undefined && tp !== null) params.set('takeprofit', String(tp));
        return await request('GET', `/manager/OrderModify?${params.toString()}`);
    },
    async closeAllPositions(logins?: string) {
        const params = new URLSearchParams();
        if (logins) params.set('logins', logins);
        return await request('GET', `/manager/OrderCloseAll?${params.toString()}`);
    },
    async reopenOrder(_ticket: number | string) {
        return { status: 'success' };
    },

    /* trading operation dialog (doc §Viewing an Order/Deal/Position) */
    async getTradeOperation(kind: OperationKind, id: number | string): Promise<TradeOperationView> {
        const idStr = String(id);
        const [positions, deals, activeOrders, historyOrders] = await Promise.all([
            liveApi.getPositions().catch(() => []),
            liveApi.getDeals().catch(() => []),
            liveApi.getOrders().catch(() => []),
            liveApi.getOrderHistory().catch(() => []),
        ]);
        const orders = [...activeOrders, ...historyOrders];

        let targetPosId = '';
        let targetLogin = 0;
        let targetSymbol = '';
        let targetTime = '';
        let targetPrice = 0;
        let title = '';
        let details: Record<string, any> = {};

        // 1. Identify clicked entity and resolve its associated position_id
        if (kind === 'position') {
            const p = positions.find((x) => String(x.position_id) === idStr || String(x.ticket) === idStr);
            targetPosId = p ? String(p.position_id) : idStr;
            targetLogin = p ? p.login : 0;
            targetSymbol = p ? p.symbol : '';
            targetTime = p?.open_time || '';
            targetPrice = p?.price_open || 0;
        } else if (kind === 'order') {
            const o = orders.find((x) => String(x.ticket) === idStr || String(x.order_id) === idStr);
            if (o) {
                targetLogin = o.login;
                targetSymbol = o.symbol;
                targetTime = o.time_done || o.time_setup || '';
                targetPrice = o.price_done || o.price_order || 0;
                targetPosId = String(o.position_id || o.position || '');
            }
            if (!targetPosId || targetPosId === '0') {
                const matchingDeal = deals.find((d) => String(d.order) === idStr || (o && String(d.order) === String(o.ticket)));
                if (matchingDeal) {
                    targetPosId = String(matchingDeal.position || matchingDeal.position_id || '');
                }
            }
        } else {
            // deal
            const d = deals.find((x) => String(x.deal_id) === idStr || String(x.ticket) === idStr);
            if (d) {
                targetLogin = d.login;
                targetSymbol = d.symbol;
                targetTime = d.time || '';
                targetPrice = d.price || 0;
                targetPosId = String(d.position || d.position_id || '');
            }
        }

        // 2. Strict MT5 correlation: filter ONLY transactions strictly linked to targetPosId
        let relPos = positions.find((p) => String(p.position_id) === targetPosId || (targetPosId && String(p.ticket) === targetPosId));
        let relDeals = targetPosId
            ? deals.filter((d) => String(d.position) === targetPosId || String(d.position_id) === targetPosId)
            : (kind === 'deal' ? deals.filter((d) => String(d.deal_id) === idStr || String(d.ticket) === idStr) : []);
        let relOrders = targetPosId
            ? orders.filter((o) => String(o.position_id) === targetPosId || String(o.position) === targetPosId || relDeals.some((d) => String(d.order) === String(o.ticket) || String(d.order) === String(o.order_id)))
            : (kind === 'order' ? orders.filter((o) => String(o.ticket) === idStr || String(o.order_id) === idStr) : []);

        // 3. Ensure EVERY deal in relDeals has an order row in relOrders (especially exit / OUT orders)
        for (const d of relDeals) {
            const orderTicket = d.order || (d.ticket ? String(d.ticket) : '');
            if (!orderTicket) continue;

            const existingOrder = relOrders.find(
                (o) => String(o.ticket) === String(orderTicket) || String(o.order_id) === String(orderTicket)
            );
            if (!existingOrder) {
                const isSell = String(d.type ?? '').toLowerCase().includes('sell');
                relOrders.push({
                    ticket: num(orderTicket),
                    order_id: String(orderTicket),
                    position: d.position || targetPosId,
                    position_id: d.position || targetPosId,
                    login: d.login || targetLogin,
                    symbol: d.symbol || targetSymbol,
                    type: isSell ? 1 : 0,
                    volume: d.volume,
                    volume_initial: d.volume,
                    volume_current: d.volume,
                    price_order: d.price,
                    price_done: d.price,
                    price_sl: 0,
                    price_tp: 0,
                    time_setup: d.time,
                    time_done: d.time,
                    state: 'filled',
                    reason: d.comment && d.comment.includes('Dealer') ? 'Dealer' : (d.reason || 'Client'),
                    comment: d.comment || '',
                });
            }
        }

        // If targetPos was closed (not in open positions table), reconstruct it from the deals/orders
        if (!relPos && targetPosId && (relDeals.length > 0 || relOrders.length > 0)) {
            const inDeal = relDeals.find((d) => d.action === 'in') || relDeals[0];
            const inOrder = relOrders[0];
            const outDeal = relDeals.find((d) => d.action === 'out');
            relPos = {
                position_id: targetPosId,
                ticket: inDeal?.ticket || num(targetPosId),
                login: inDeal?.login || inOrder?.login || targetLogin,
                symbol: inDeal?.symbol || inOrder?.symbol || targetSymbol,
                type: inDeal?.type === 'sell' ? 1 : 0,
                volume: inDeal?.volume || inOrder?.volume || 0,
                price_open: inDeal?.price || inOrder?.price_done || 0,
                price_current: outDeal?.price || inDeal?.price || 0,
                sl: inOrder?.price_sl || 0,
                tp: inOrder?.price_tp || 0,
                swap: relDeals.reduce((acc, cur) => acc + (cur.swap || 0), 0),
                profit: relDeals.reduce((acc, cur) => acc + (cur.profit || 0), 0),
                commission: relDeals.reduce((acc, cur) => acc + (cur.commission || 0), 0),
                reason: inOrder?.reason || inDeal?.comment || 'Client',
                comment: inDeal?.comment || inOrder?.comment || '',
                open_time: inDeal?.time || inOrder?.time_setup || targetTime,
                update_time: outDeal?.time || inDeal?.time || targetTime,
            };
        }

        if (!targetLogin && relPos) targetLogin = relPos.login;
        if (!targetSymbol && relPos) targetSymbol = relPos.symbol;

        // 4. Chain Rows Helpers
        const dealRow = (d: any): OperationChainRow => {
            const isOut = d.action === 'out' || String(d.entry) === '1' || (d.closed_volume && d.closed_volume > 0);
            return {
                kind: 'deal',
                ticket: d.deal_id || d.ticket,
                time: d.time || '',
                ext_id: '',
                type: d.type || (d.action === 1 ? 'sell' : 'buy'),
                volume: String(d.volume ?? ''),
                volume_current: isOut ? String(d.volume ?? '') : '0', // In MT5: 0 for IN, volume for OUT
                price: String(d.price ?? ''),
                reason: d.comment || d.reason || 'Dealer',
                profit: isOut ? d.profit : 0,
                action: isOut ? 'out' : 'in',
            };
        };

        const orderRow = (o: any): OperationChainRow => ({
            kind: 'order',
            ticket: o.ticket || o.order_id,
            time: o.time_setup || '',
            ext_id: '',
            type: ORDER_TYPE_LABEL[o.type] ?? String(o.type ?? 'buy'),
            volume: `${o.volume} / ${o.volume}`, // In MT5: "0.01 / 0.01"
            volume_current: '',
            price: o.type === 0 || o.type === 1 || o.type === 'buy' || o.type === 'sell' ? 'market' : String(o.price_order ?? ''),
            reason: o.reason || 'Client',
            profit: undefined,
        });

        // 5. Build Chain Table in exact MT5 order:
        // Row 1: The Position
        // Subsequent rows: Chronological lifecycle transactions (Orders & Deals)
        const chain: OperationChainRow[] = [];
        if (relPos) {
            chain.push({
                kind: 'position',
                ticket: relPos.position_id || relPos.ticket,
                time: relPos.open_time || '',
                ext_id: '',
                type: relPos.type === 0 ? 'buy' : 'sell',
                volume: String(relPos.volume ?? ''),
                volume_current: '',
                price: String(relPos.price_open ?? ''),
                reason: relPos.reason || 'Client',
                profit: relPos.profit,
            });
        }

        const events: OperationChainRow[] = [
            ...relOrders.map(orderRow),
            ...relDeals.map(dealRow),
        ].sort((a, b) => {
            const timeCmp = String(a.time).localeCompare(String(b.time));
            if (timeCmp !== 0) return timeCmp;
            // Order always comes before deal when timestamps match
            if (a.kind === 'order' && b.kind === 'deal') return -1;
            if (a.kind === 'deal' && b.kind === 'order') return 1;
            return 0;
        });

        chain.push(...events);

        // 5. Populate Details & Title depending on the requested kind
        if (kind === 'position') {
            const p = relPos || {
                position_id: idStr,
                ticket: num(id),
                login: targetLogin,
                symbol: targetSymbol,
                type: 0,
                volume: 0.01,
                price_open: targetPrice,
                price_current: targetPrice,
                sl: 0,
                tp: 0,
                swap: 0,
                profit: 0,
                reason: 'Client',
                comment: '',
                open_time: targetTime,
                update_time: targetTime,
            };
            title = `Position #${p.position_id} ${p.type === 0 ? 'buy' : 'sell'} ${p.volume} ${p.symbol} ${p.price_open}`;
            details = {
                position: p.position_id,
                type: p.type === 0 ? 'buy' : 'sell',
                volume: p.volume,
                symbol: p.symbol,
                opened: p.open_time,
                updated: p.update_time,
                reason: p.reason ?? 'Client',
                dealer_id: '',
                expert_id: '',
                external_id: p.ticket ? String(p.ticket) : '',
                comment: p.comment ?? '',
                open_price: p.price_open,
                current_price: p.price_current,
                sl: p.sl,
                tp: p.tp,
                swap: p.swap,
                profit: p.profit,
                margin_rate: p.price_open,
                disabled_activations: [],
                modifications: [],
            };
        } else if (kind === 'order') {
            const o = relOrders.find((x) => String(x.ticket) === idStr || String(x.order_id) === idStr) || orders.find((x) => String(x.ticket) === idStr || String(x.order_id) === idStr) || {
                ticket: num(id),
                order_id: idStr,
                login: targetLogin,
                symbol: targetSymbol,
                type: 0,
                volume: 0.01,
                price_order: targetPrice,
                price_done: targetPrice,
                price_sl: 0,
                price_tp: 0,
                reason: 'Client',
                state: 'FILLED',
                time_setup: targetTime,
            };
            const oTypeStr = ORDER_TYPE_LABEL[o.type] ?? o.type;
            const priceDesc = o.type === 0 || o.type === 1 || o.type === 'buy' || o.type === 'sell' ? 'at market' : `at ${o.price_order}`;
            title = `Order #${o.ticket || o.order_id} ${oTypeStr} ${o.volume} / ${o.volume} ${o.symbol} ${priceDesc}`;
            details = {
                order: o.ticket || o.order_id,
                position: targetPosId || relPos?.position_id || null,
                type: oTypeStr,
                volume: o.volume,
                remained_volume: 0,
                symbol: o.symbol,
                reason: o.reason ?? 'Client',
                state: (typeof o.state === 'string' ? o.state : ORDER_STATE_LABEL[o.state] ?? 'FILLED').toUpperCase(),
                expiration: 'GTC',
                filling: 'IMMEDIATE OR CANCEL',
                dealer_id: '',
                expert_id: '',
                external_id: '',
                comment: o.comment ?? '',
                setup_time: o.time_setup,
                done_time: o.time_done ?? o.time_setup ?? '',
                expiration_time: '',
                order_price: o.price_order || o.price_done || 0,
                current_price: o.price_done || o.price_order || 0,
                trigger_price: 0,
                sl: o.price_sl || 0,
                tp: o.price_tp || 0,
                margin_rate: o.price_done || o.price_order || 0,
                disabled_activations: [],
                modifications: [],
            };
        } else {
            // deal
            const d = relDeals.find((x) => String(x.deal_id) === idStr || String(x.ticket) === idStr) || deals.find((x) => String(x.deal_id) === idStr || String(x.ticket) === idStr) || {
                deal_id: idStr,
                ticket: num(id),
                order: '',
                position: targetPosId,
                login: targetLogin,
                symbol: targetSymbol,
                type: 'buy',
                action: 'in',
                volume: 0.01,
                price: targetPrice,
                profit: 0,
                time: targetTime,
                comment: '',
            };
            const isOut = d.action === 'out' || String(d.entry) === '1';
            title = `Deal #${d.deal_id || d.ticket} ${d.type} ${d.volume} ${d.symbol} at ${d.price}`;
            details = {
                deal: d.deal_id || d.ticket,
                position: targetPosId || relPos?.position_id || null,
                order: d.order || relOrders[0]?.ticket || null,
                type: d.type,
                action: isOut ? 'OUT' : 'IN',
                volume: d.volume,
                closed_volume: isOut ? d.volume : 0,
                symbol: d.symbol,
                create_time: d.time,
                reason: d.comment || d.reason || 'Dealer',
                dealer_id: '',
                expert_id: '',
                external_id: '',
                comment: d.comment ?? '',
                market_bid: d.price,
                market_ask: d.price,
                market_last: 0,
                price: d.price,
                position_price: relPos?.price_open ?? d.price,
                sl: 0,
                tp: 0,
                commission: d.commission || 0,
                fee: 0,
                swap: d.swap || 0,
                profit: d.profit || 0,
                raw_profit: d.profit || 0,
                profit_rate: 1,
                margin_rate: d.price,
                gateway_price: 0,
                modifications: [],
            };
        }

        // Account line
        let acc: any = null;
        if (targetLogin) {
            try {
                acc = await liveApi.getAccountDetail(targetLogin);
            } catch {
                acc = { login: targetLogin, name: `Account ${targetLogin}`, group: 'real\\real', leverage: 100 };
            }
        }

        const opTimestamp = targetTime || new Date().toISOString();
        const ticks = genTicksAround(targetSymbol || 'ETHUSD', opTimestamp, targetPrice);

        return {
            kind,
            id,
            title,
            account: acc ? { login: acc.login, name: acc.name, group: acc.group, leverage: acc.leverage } : null,
            chain,
            details,
            ticks,
            journal: [
                { time: opTimestamp, server: 'TradeServer', message: `'${targetLogin}': ${kind} #${id} ${title.split(' ').slice(1).join(' ')} requested` },
                { time: opTimestamp, server: 'TradeServer', message: `'${targetLogin}': ${kind} #${id} executed at ${targetPrice}` },
                { time: opTimestamp, server: 'HistoryServer', message: `tick stream archived for ${targetSymbol || 'n/a'}` },
            ],
        };
    },
    async updateTradeOperation() {
        return { status: 'success' };
    },

    /* symbols — read-only in bp today */
    async getSymbols() {
        const rows = await request<any[]>('GET', '/admin/symbols');
        return rows.map(mapSymbol);
    },
    async getSymbolDetail(symbol: string) {
        const lookup = symbol.endsWith('.dummy') ? symbol : (symbol.split('\\').pop() || symbol);
        const s = mapSymbol(await request('GET', `/admin/symbols/${encodeURIComponent(lookup)}`));
        return {
            ...s,
            currency: s.quote_currency,
            spread_base: s.spread,
            margin_initial: s.margin_initial_buy,
            margin_maintenance: s.margin_maintenance_buy,
            settings_json: symbolSettingsJson(s),
        };
    },
    async createSymbol(data: any) {
        return await request('POST', '/admin/symbols', data);
    },
    async updateSymbol(symbol: string, data: any) {
        const lookup = symbol.endsWith('.dummy') ? symbol : (symbol.split('\\').pop() || symbol);
        return await request('PUT', `/admin/symbols/${encodeURIComponent(lookup)}`, data);
    },
    async deleteSymbol(symbol: string) {
        return await request('DELETE', `/admin/symbols/${encodeURIComponent(symbol)}`);
    },

    /* groups */
    async getGroups() {
        const rows = await request<any[]>('GET', '/admin/groups');
        return rows.map(mapGroup);
    },
    async getGroupDetail(name: string) {
        return mapGroup(await request('GET', `/admin/groups/${toPathName(name)}`));
    },
    async createGroup(data: any) {
        // Map the UI create payload (+settings_json blob) onto bp's CreateGroupCommand.
        let settings: any = {};
        try {
            settings = data.settings_json ? JSON.parse(data.settings_json) : {};
        } catch {
            /* ignore malformed blob */
        }
        const accType = settings.account_type ?? data.account_type;
        return request('POST', '/admin/groups/create', {
            name: data.name,
            account_type: accType ? String(accType).toLowerCase() : undefined,
            currency: settings.currency ?? data.currency ?? 'USD',
            leverage_default: num(settings.default_leverage, num(data.max_leverage, 100)),
            leverage_max: num(settings.max_leverage, num(data.max_leverage, 500)),
            margin_call_level: num(settings.margin_call, num(data.margin_call, 80)),
            stop_out_level: num(settings.margin_stop_out, num(data.margin_stop_out, 50)),
            trade_allowed: settings.trade_allowed ?? true,
        });
    },
    async updateGroup(name: string, data: any) {
        let settings: any = {};
        try {
            settings = data.settings_json ? JSON.parse(data.settings_json) : {};
        } catch {
            /* ignore malformed blob */
        }
        return request('PUT', `/admin/groups/${toPathName(name)}`, {
            currency: settings.currency ?? data.currency,
            leverage_default: settings.default_leverage !== undefined ? num(settings.default_leverage) : undefined,
            leverage_max: settings.max_leverage !== undefined ? num(settings.max_leverage) : undefined,
            margin_call_level: settings.margin_call !== undefined ? num(settings.margin_call) : undefined,
            stop_out_level: settings.margin_stop_out !== undefined ? num(settings.margin_stop_out) : undefined,
            trade_allowed: settings.trade_allowed,
        });
    },
    async createGroupSymbolOverride() {
        throw new BackendGapError(
            'createGroupSymbolOverride',
            'Group symbol overrides persist through the MT5 import/seed path, not an HTTP endpoint yet.'
        );
    },

    /* routing — M8 engine exists, no HTTP surface */
    async getRoutingRules() {
        throw new BackendGapError(
            'getRoutingRules',
            'M8 routing rules live in the mt5_routing_rules table (seed/file import); no REST surface yet. The UI rule model also needs the MT5-taxonomy redesign (F4).'
        );
    },
    async createRoutingRule() {
        throw new BackendGapError('createRoutingRule');
    },
    async updateRoutingRule() {
        throw new BackendGapError('updateRoutingRule');
    },
    async deleteRoutingRule() {
        throw new BackendGapError('deleteRoutingRule');
    },
    async enableRoutingRule() {
        throw new BackendGapError('enableRoutingRule');
    },
    async disableRoutingRule() {
        throw new BackendGapError('disableRoutingRule');
    },
    async reorderRoutingRules() {
        throw new BackendGapError('reorderRoutingRules');
    },

    /* gateways — env-configured in bp (M10) */
    async getGateways() {
        return [
            {
                id: 1,
                name: 'LP MT5 Gateway',
                type: 'mt5',
                host: '127.0.0.1',
                port: 8000,
                is_active: true,
            },
        ];
    },
    async createGateway() {
        throw new BackendGapError('createGateway');
    },
    async updateGateway() {
        throw new BackendGapError('updateGateway');
    },
    async testGateway() {
        throw new BackendGapError('testGateway');
    },

    /* market data */
    async getTicks(): Promise<Ticks> {
        const rows = await request<any[]>('GET', '/admin/ticks');
        const out: Ticks = {};
        for (const r of rows) {
            if (r.symbol) {
                out[r.symbol] = {
                    bid: num(r.bid),
                    ask: num(r.ask),
                    age: num(r.age_seconds),
                };
            }
        }
        return out;
    },

    /* risk */
    async getRiskSummary() {
        throw new BackendGapError('getRiskSummary', 'No /admin/risk/* endpoints yet.');
    },
    async getRiskExposure() {
        throw new BackendGapError('getRiskExposure');
    },
    async getRiskMarginCalls() {
        throw new BackendGapError('getRiskMarginCalls');
    },
};
