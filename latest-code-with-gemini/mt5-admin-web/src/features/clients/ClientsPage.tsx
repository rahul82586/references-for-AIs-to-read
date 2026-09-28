import * as React from 'react';
import { API, isBackendGap } from '../../services/api';
import { AccountsTable } from './AccountsTable';
import { ClientsTable } from './ClientsTable';
import { ManagersTable } from './ManagersTable';
import { AllocationsPanel } from './AllocationsPanel';
import { AccountEditModal } from './AccountEditModal';
import { AccountNewModal } from './AccountNewModal';
import { ClientModal } from './ClientModal';
import { ManagerModal } from './ManagerModal';
import { ContextMenu, MenuItem } from './Menu';
import { toCsv, downloadCsv } from './format';

type Tab = 'accounts' | 'clients' | 'managers' | 'allocations';

interface Props {
    initialTab?: Tab;
    /** pre-filled request bar (e.g. a login pushed from another panel) */
    initialRequest?: string;
    close?(): void;
}

interface Banner { kind: 'error' | 'gap' | 'info'; text: string }

/**
 * Clients & Accounts section — four DIFFERENT entities, per MT5 Administrator:
 *  · Trading Accounts — every account type (type follows the group); double-
 *    click opens the 7-tab editing window; New opens the separate create dialog
 *  · Clients   — backoffice records (KYC, documents, versions)
 *  · Managers  — permissions & access (rights, serviced groups, IP list)
 *  · Allocations — terminal-opened account rules (URLs, country→group, agreements)
 * No folder tree pane in this section (design decision, matches MT5 window).
 */
export function ClientsPage({ initialTab = 'accounts', initialRequest = '' }: Props): React.ReactElement {
    const [tab, setTab] = React.useState<Tab>(initialTab);

    const [accounts, setAccounts] = React.useState<any[]>([]);
    const [clients, setClients] = React.useState<any[]>([]);
    const [managers, setManagers] = React.useState<any[]>([]);
    const [allocations, setAllocations] = React.useState<any>(null);
    const [groups, setGroups] = React.useState<any[]>([]);

    const [loading, setLoading] = React.useState(true);
    const [banner, setBanner] = React.useState<Banner | null>(null);

    const [request, setRequest] = React.useState(initialRequest);
    const [requestGroup, setRequestGroup] = React.useState('');

    const [selectedAccounts, setSelectedAccounts] = React.useState<number[]>([]);
    const [selectedClients, setSelectedClients] = React.useState<string[]>([]);
    const [selectedManagers, setSelectedManagers] = React.useState<number[]>([]);

    const [menu, setMenu] = React.useState<{ x: number; y: number; items: MenuItem[] } | null>(null);
    const [newAccount, setNewAccount] = React.useState(false);
    const [editLogin, setEditLogin] = React.useState<number | null>(null);
    const [clientOpen, setClientOpen] = React.useState<any | null>(null);
    const [managerOpen, setManagerOpen] = React.useState<any | null>(null);

    const notify = (b: Banner) => setBanner(b);
    const err = (e: any) => notify(isBackendGap(e) ? { kind: 'gap', text: e.message } : { kind: 'error', text: String(e?.message ?? e) });

    /* ---------------- loading ---------------- */

    const loadTab = React.useCallback(async (t: Tab) => {
        setLoading(true);
        setBanner(null);
        try {
            if (t === 'accounts') setAccounts(await API.getAccounts());
            if (t === 'clients') setClients(await API.getClients());
            if (t === 'managers') setManagers(await API.getManagers());
            if (t === 'allocations') setAllocations(await API.getAllocations());
        } catch (e) {
            err(e);
        } finally {
            setLoading(false);
        }
    }, []);

    React.useEffect(() => {
        API.getGroups().then(setGroups).catch(() => setGroups([]));
    }, []);

    React.useEffect(() => {
        if (initialRequest) setRequest(initialRequest);
    }, [initialRequest]);

    React.useEffect(() => {
        setSelectedAccounts([]);
        setSelectedClients([]);
        setSelectedManagers([]);
        void loadTab(tab);
    }, [tab, loadTab]);

    /* ---------------- request bar filtering (display-side) ---------------- */

    const filteredAccounts = React.useMemo(() => {
        let rows = accounts;
        if (requestGroup) rows = rows.filter((a) => a.group === requestGroup);
        const q = request.trim();
        if (q && q !== '*') {
            const parts = q.split(',').map((s) => s.trim()).filter(Boolean);
            const exact = parts.filter((p) => /^\d+$/.test(p)).map(Number);
            const masks = parts.filter((p) => !/^\d+$/.test(p));
            rows = rows.filter((a) => {
                if (exact.includes(a.login)) return true;
                const hay = `${a.login} ${a.name ?? ''} ${a.group ?? ''}`.toLowerCase();
                return masks.some((m) => hay.includes(m.toLowerCase()) ||
                    new RegExp(`^${m.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\\\*/g, '.*')}$`).test(hay));
            });
        }
        return rows;
    }, [accounts, request, requestGroup]);

    const filteredClients = React.useMemo(() => {
        const q = request.trim().toLowerCase();
        if (!q || q === '*') return clients;
        return clients.filter((c) => `${c.id} ${c.first_name} ${c.last_name} ${c.email} ${c.phone} ${c.company}`.toLowerCase().includes(q));
    }, [clients, request]);

    const filteredManagers = React.useMemo(() => {
        const q = request.trim().toLowerCase();
        if (!q || q === '*') return managers;
        return managers.filter((m) => `${m.login} ${m.name} ${m.mailbox}`.toLowerCase().includes(q));
    }, [managers, request]);

    /* ---------------- shared actions ---------------- */

    const gap = (what: string) => notify({ kind: 'gap', text: `Backend gap: ${what} is not exposed by the API yet.` });

    const copyText = async (text: string, what: string) => {
        try {
            await navigator.clipboard.writeText(text);
            notify({ kind: 'info', text: `Copied ${what} to clipboard.` });
        } catch {
            notify({ kind: 'error', text: 'Clipboard unavailable in this browser context.' });
        }
    };

    const exportAccountsCsv = () => {
        const rows = filteredAccounts.filter((a) => selectedAccounts.length === 0 || selectedAccounts.includes(a.login));
        downloadCsv(`accounts_${new Date().toISOString().slice(0, 10)}.csv`, toCsv(rows, [
            { key: 'login', label: 'Login' }, { key: 'name', label: 'Name' }, { key: 'account_type', label: 'Type' },
            { key: 'group', label: 'Group' }, { key: 'currency', label: 'Currency' }, { key: 'balance', label: 'Balance' },
            { key: 'credit', label: 'Credit' }, { key: 'equity', label: 'Equity' }, { key: 'margin', label: 'Margin' },
            { key: 'margin_free', label: 'FreeMargin' }, { key: 'margin_level', label: 'MarginLevel' }, { key: 'leverage', label: 'Leverage' },
        ]));
        notify({ kind: 'info', text: `Exported ${rows.length} account(s) to CSV.` });
    };

    const removeAccounts = async (logins: number[]) => {
        if (!window.confirm(`Delete account(s) ${logins.join(', ')}?\nTrade history is NOT deleted (doc §Accounts).`)) return;
        try {
            for (const l of logins) await API.deleteAccount(l);
            notify({ kind: 'info', text: `Deleted account(s) ${logins.join(', ')}.` });
            void loadTab('accounts');
        } catch (e) {
            err(e);
        }
    };

    const openGroupOf = (login: number) => {
        const acc = accounts.find((a) => a.login === login);
        if (!acc?.group) return;
        window.dispatchEvent(new CustomEvent('mt5-admin:open-node', { detail: { id: `groups:${acc.group}`, label: 'Groups' } }));
    };

    /* ---------------- context menus (doc command sets) ---------------- */

    const accountMenu = (login: number | null): MenuItem[] => [
        { id: 'new', label: 'New Account…', icon: 'add', onClick: () => setNewAccount(true) },
        ...(login !== null
            ? [
                  { id: 'edit', label: 'Edit (7-tab window)', icon: 'edit', onClick: () => setEditLogin(login) },
                  { id: 'editgroup', label: 'Edit Group', icon: 'organization', onClick: () => openGroupOf(login) },
                  { id: 'editmanager', label: 'Edit Manager', icon: 'account', onClick: () => setTab('managers') },
                  { id: 'toggle', label: 'Enable / Disable', icon: 'lock', gap: true, onClick: () => gap('Enable/disable account') },
                  { id: 'del', label: 'Delete', icon: 'trash', danger: true, onClick: () => void removeAccounts([login]) },
                  { id: 's1', sep: true },
                  { id: 'checkbal', label: 'Check Balance', icon: 'check', gap: true, onClick: () => gap('Check Balance') },
                  { id: 'fixbal', label: 'Fix Balance', icon: 'wrench', gap: true, onClick: () => gap('Fix Balance') },
                  { id: 'archive', label: 'Move to Archive', icon: 'archive', gap: true, onClick: () => gap('Move to Archive') },
              ]
            : []),
        { id: 's2', sep: true },
        {
            id: 'copylines', label: 'Copy as Lines', icon: 'copy',
            onClick: () => {
                const rows = filteredAccounts.filter((a) => (login !== null ? a.login === login : selectedAccounts.includes(a.login)));
                void copyText(rows.map((r) => Object.values(r).join('\t')).join('\n'), 'rows');
            },
        },
        {
            id: 'copylogins', label: 'Copy List of Logins', icon: 'copy',
            onClick: () => {
                const rows = filteredAccounts.filter((a) => (login !== null ? a.login === login : selectedAccounts.includes(a.login)));
                void copyText(rows.map((r) => r.login).join(','), 'logins');
            },
        },
        { id: 'export', label: 'Export CSV…', icon: 'export', onClick: exportAccountsCsv },
        { id: 's3', sep: true },
        { id: 'impfile', label: 'Import from File…', icon: 'file-add', gap: true, onClick: () => gap('Import from File') },
        { id: 'impsrv', label: 'Import from Server…', icon: 'cloud-download', gap: true, onClick: () => gap('Import from Server') },
    ];

    const clientMenu = (id: string | null): MenuItem[] => [
        { id: 'newc', label: 'New Client…', icon: 'add', gap: true, onClick: () => gap('New Client (write)') },
        ...(id
            ? [
                  { id: 'editc', label: 'Edit Client Record…', icon: 'edit', gap: true, onClick: () => gap('Client record writes') },
                  {
                      id: 'viewacc', label: 'View Trading Accounts', icon: 'credit-card',
                      onClick: () => {
                          const c = clients.find((x) => x.id === id);
                          setRequest((c?.accounts ?? []).map(String).join(',') || '*');
                          setTab('accounts');
                      },
                  },
                  { id: 'copymail', label: 'Copy Email', icon: 'mail', onClick: () => void copyText(clients.find((x) => x.id === id)?.email ?? '', 'email') },
              ]
            : []),
    ];

    const managerMenu = (login: number | null): MenuItem[] => [
        { id: 'addm', label: 'Add Manager…', icon: 'add', gap: true, onClick: () => gap('Manager write endpoints') },
        ...(login !== null
            ? [
                  { id: 'editm', label: 'Edit Manager…', icon: 'edit', gap: true, onClick: () => gap('Manager write endpoints') },
                  { id: 'delm', label: 'Delete Manager', icon: 'trash', danger: true, gap: true, onClick: () => gap('Manager write endpoints') },
                  { id: 'copylogin', label: 'Copy Login', icon: 'copy', onClick: () => void copyText(String(login), 'manager login') },
              ]
            : []),
    ];

    const showMenu = (items: MenuItem[]) => (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setMenu({ x: Math.min(e.clientX, window.innerWidth - 250), y: Math.min(e.clientY, window.innerHeight - 400), items });
    };

    /* ---------------- render ---------------- */

    const tabs: Array<{ id: Tab; label: string; icon: string }> = [
        { id: 'accounts', label: 'Trading Accounts', icon: 'credit-card' },
        { id: 'clients', label: 'Clients', icon: 'organization' },
        { id: 'managers', label: 'Managers', icon: 'account' },
        { id: 'allocations', label: 'Allocations', icon: 'list-selection' },
    ];

    return (
        <div className="ca-page">
            <div className="adm-tabs ca-tabs">
                {tabs.map((t) => (
                    <button key={t.id} className={`adm-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
                        <i className={`codicon codicon-${t.icon}`} /> {t.label}
                    </button>
                ))}
            </div>

            {tab !== 'allocations' && (
                <div className="ca-toolbar">
                    <div className="ca-request">
                        <i className="codicon codicon-search" />
                        <input
                            className="adm-input"
                            placeholder={tab === 'accounts' ? 'request: 50001, 5000* or * for all' : tab === 'clients' ? 'request: name, email, phone, ID or *' : 'search…'}
                            value={request}
                            onChange={(e) => setRequest(e.target.value)}
                        />
                        {tab === 'accounts' && (
                            <select className="adm-select" value={requestGroup} onChange={(e) => setRequestGroup(e.target.value)}>
                                <option value="">all groups</option>
                                {groups.map((g) => <option key={g.name} value={g.name}>{g.name}</option>)}
                            </select>
                        )}
                        <button className="wb-btn secondary" onClick={() => void loadTab(tab)} title="Request from server">
                            <i className="codicon codicon-refresh" /> Request
                        </button>
                    </div>
                    <div className="ca-toolbar-actions">
                        {tab === 'accounts' && (
                            <>
                                <button className="wb-btn" onClick={() => setNewAccount(true)}>
                                    <i className="codicon codicon-add" /> New
                                </button>
                                <button className="wb-btn secondary" disabled={selectedAccounts.length !== 1} onClick={() => setEditLogin(selectedAccounts[0])}>
                                    <i className="codicon codicon-edit" /> Edit
                                </button>
                                <button className="wb-btn secondary ca-danger" disabled={selectedAccounts.length === 0} onClick={() => void removeAccounts(selectedAccounts)}>
                                    <i className="codicon codicon-trash" /> Delete
                                </button>
                            </>
                        )}
                        <span className="ca-count">
                            {loading
                                ? 'requesting…'
                                : tab === 'accounts'
                                    ? `${filteredAccounts.length} of ${accounts.length} accounts`
                                    : tab === 'clients'
                                        ? `${filteredClients.length} of ${clients.length} clients`
                                        : `${filteredManagers.length} of ${managers.length} managers`}
                        </span>
                    </div>
                </div>
            )}

            {banner && (
                <div className={`ca-banner ${banner.kind}`}>
                    <i className={`codicon codicon-${banner.kind === 'info' ? 'info' : 'warning'}`} />
                    <span>{banner.text}</span>
                    <button className="adm-icon-btn" onClick={() => setBanner(null)}><i className="codicon codicon-close" /></button>
                </div>
            )}

            <div className="ca-main">
                {tab === 'accounts' && (
                    <AccountsTable
                        rows={filteredAccounts}
                        selected={selectedAccounts}
                        onSelect={(logins, e) =>
                            setSelectedAccounts(e.ctrlKey || e.metaKey
                                ? (selectedAccounts.includes(logins[0])
                                    ? selectedAccounts.filter((l) => l !== logins[0])
                                    : [...selectedAccounts, ...logins])
                                : logins)
                        }
                        onOpen={(l) => setEditLogin(l)}
                        onContext={(login, e) => {
                            if (login !== null && !selectedAccounts.includes(login)) setSelectedAccounts([login]);
                            showMenu(accountMenu(login))(e);
                        }}
                    />
                )}
                {tab === 'clients' && (
                    <ClientsTable
                        rows={filteredClients}
                        selected={selectedClients}
                        onSelect={(ids) => setSelectedClients(ids)}
                        onContext={(id, e) => showMenu(clientMenu(id))(e)}
                        onOpen={(id) => setClientOpen(clients.find((x) => x.id === id) ?? null)}
                        onViewAccounts={(id) => {
                            const c = clients.find((x) => x.id === id);
                            setRequest((c?.accounts ?? []).map(String).join(',') || '*');
                            setTab('accounts');
                        }}
                    />
                )}
                {tab === 'managers' && (
                    <ManagersTable
                        rows={filteredManagers}
                        selected={selectedManagers}
                        onSelect={(ls) => setSelectedManagers(ls)}
                        onContext={(login, e) => showMenu(managerMenu(login))(e)}
                        onOpen={(l) => setManagerOpen(managers.find((x) => x.login === l) ?? null)}
                    />
                )}
                {tab === 'allocations' && (
                    <AllocationsPanel settings={allocations} onError={(m, g) => notify(g ? { kind: 'gap', text: m } : { kind: 'error', text: m })} onInfo={(m) => notify({ kind: 'info', text: m })} />
                )}
            </div>

            {menu && <ContextMenu x={menu.x} y={menu.y} items={menu.items} onClose={() => setMenu(null)} />}
            {newAccount && (
                <AccountNewModal
                    onClose={() => setNewAccount(false)}
                    onSaved={(m) => { setNewAccount(false); notify({ kind: 'info', text: m }); void loadTab('accounts'); }}
                    onError={(m, g) => notify(g ? { kind: 'gap', text: m } : { kind: 'error', text: m })}
                />
            )}
            {editLogin !== null && (
                <AccountEditModal
                    login={editLogin}
                    onClose={() => setEditLogin(null)}
                    onSaved={(m) => { setEditLogin(null); notify({ kind: 'info', text: m }); void loadTab('accounts'); }}
                    onError={(m, g) => notify(g ? { kind: 'gap', text: m } : { kind: 'error', text: m })}
                    onOpenClient={(cid) => {
                        setEditLogin(null);
                        const c = clients.find((x) => x.id === cid);
                        if (c) setClientOpen(c);
                        else setTab('clients');
                    }}
                />
            )}
            {clientOpen && <ClientModal client={clientOpen} onClose={() => setClientOpen(null)} onOpenAccount={(l) => { setClientOpen(null); setEditLogin(l); }} onError={(m, g) => notify(g ? { kind: 'gap', text: m } : { kind: 'error', text: m })} />}
            {managerOpen && <ManagerModal manager={managerOpen} onClose={() => setManagerOpen(null)} onError={(m, g) => notify(g ? { kind: 'gap', text: m } : { kind: 'error', text: m })} />}
        </div>
    );
}
