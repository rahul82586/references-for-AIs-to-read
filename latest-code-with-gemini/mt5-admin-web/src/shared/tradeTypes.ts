/** MT5 trade-operation enums → display strings (rendering only). */
export const ORDER_TYPE: Record<number, string> = {
    0: 'buy', 1: 'sell', 2: 'buy limit', 3: 'sell limit', 4: 'buy stop', 5: 'sell stop',
};
export const ORDER_STATE: Record<number | string, string> = {
    0: 'placed', 1: 'partial', 4: 'filled', 5: 'canceled', 6: 'dealer', 7: 'gateway',
    filled: 'filled', canceled: 'canceled', rejected: 'rejected', placed: 'placed',
};
export const ORDER_ICON: Record<number, { icon: string; cls: string }> = {
    0: { icon: 'arrow-up', cls: 'heat-green' },
    1: { icon: 'arrow-down', cls: 'heat-red' },
    2: { icon: 'arrow-up', cls: 'ca-pending' },
    3: { icon: 'arrow-down', cls: 'ca-pending' },
    4: { icon: 'arrow-up', cls: 'ca-pending' },
    5: { icon: 'arrow-down', cls: 'ca-pending' },
};

export const DEAL_ICON: Record<string, { icon: string; cls: string }> = {
    buy: { icon: 'arrow-up', cls: 'heat-green' },
    sell: { icon: 'arrow-down', cls: 'heat-red' },
    balance: { icon: 'add', cls: 'heat-green' },
    credit: { icon: 'add', cls: 'heat-green' },
    charge: { icon: 'remove', cls: 'heat-red' },
    commission: { icon: 'remove', cls: 'ca-pending' },
    'daily commission': { icon: 'remove', cls: 'ca-pending' },
    'monthly commission': { icon: 'remove', cls: 'ca-pending' },
    swap: { icon: 'history', cls: 'ca-pending' },
    correction: { icon: 'edit', cls: 'ca-pending' },
    bonus: { icon: 'gift', cls: 'heat-green' },
    cancel: { icon: 'close', cls: 'heat-red' },
};

export const POSITION_ICON: Record<number, { icon: string; cls: string }> = {
    0: { icon: 'arrow-up', cls: 'heat-green' },
    1: { icon: 'arrow-down', cls: 'heat-red' },
};

/** "2025-05-19 04:24:03" like the admin terminal */
export const fmtTime = (iso?: string): string => {
    if (!iso) return '';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    const p = (n: number, w = 2) => String(n).padStart(w, '0');
    return `${d.getFullYear()}.${p(d.getMonth() + 1)}.${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
};
