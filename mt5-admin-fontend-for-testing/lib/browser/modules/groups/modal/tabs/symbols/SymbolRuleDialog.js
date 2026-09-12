"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SymbolRuleDialog = void 0;
const React = require("react");
function SymbolRuleDialog({ rule, onClose, onSave, availableSymbols }) {
    const [activeTab, setActiveTab] = React.useState('common');
    const [error, setError] = React.useState(null);
    // --- State declarations ---
    // Common Tab
    const [symbol, setSymbol] = React.useState(rule ? rule.symbol : '*');
    const [enableDom, setEnableDom] = React.useState(rule?.enable_dom ?? true);
    const [domLimit, setDomLimit] = React.useState(rule?.dom_limit ?? 'unlimited');
    const [useDefaultSpreads, setUseDefaultSpreads] = React.useState(rule?.use_default_spreads ?? true);
    const [spreadDiff, setSpreadDiff] = React.useState(rule ? String(rule.spread_diff) : '0');
    const [diffBalance, setDiffBalance] = React.useState(rule?.diff_balance ?? '1.5/1.5');
    const [useDefaultVolumes, setUseDefaultVolumes] = React.useState(rule?.use_default_volumes ?? true);
    const [volMin, setVolMin] = React.useState(rule ? String(rule.vol_min ?? 0.01) : '0.01');
    const [volStep, setVolStep] = React.useState(rule ? String(rule.vol_step ?? 0.01) : '0.01');
    const [volMax, setVolMax] = React.useState(rule ? String(rule.vol_max ?? 100.0) : '100.0');
    const [useDefaultLimit, setUseDefaultLimit] = React.useState(rule?.use_default_limit ?? true);
    const [volLimit, setVolLimit] = React.useState(rule ? String(rule.vol_limit ?? 0.0) : '0.0');
    // Trade Tab
    const [useDefaultTrade, setUseDefaultTrade] = React.useState(rule?.use_default_trade ?? true);
    const [tradeMode, setTradeMode] = React.useState(rule?.trade_mode ?? 'full'); // full, close, long, short, disabled
    const [fillingFok, setFillingFok] = React.useState(rule?.filling_fok ?? true);
    const [fillingIoc, setFillingIoc] = React.useState(rule?.filling_ioc ?? true);
    const [fillingBoc, setFillingBoc] = React.useState(rule?.filling_boc ?? false);
    const [expirationGtc, setExpirationGtc] = React.useState(rule?.expiration_gtc ?? true);
    const [expirationDay, setExpirationDay] = React.useState(rule?.expiration_day ?? true);
    const [expirationTime, setExpirationTime] = React.useState(rule?.expiration_time ?? false);
    const [expirationDate, setExpirationDate] = React.useState(rule?.expiration_date ?? false);
    const [useDefaultTradeLevels, setUseDefaultTradeLevels] = React.useState(rule?.use_default_trade_levels ?? true);
    const [limitStopLevel, setLimitStopLevel] = React.useState(rule ? String(rule.limit_stop_level ?? 0) : '0');
    const [freezeLevel, setFreezeLevel] = React.useState(rule ? String(rule.freeze_level ?? 0) : '0');
    // Execution Tab
    const [useDefaultExecution, setUseDefaultExecution] = React.useState(rule?.use_default_execution ?? true);
    const [execMode, setExecMode] = React.useState(rule?.exec_mode ?? 'market'); // instant, request, market, exchange
    const [instantMaxTimeDev, setInstantMaxTimeDev] = React.useState(rule ? String(rule.instant_max_time_dev ?? 0) : '0');
    const [instantMaxProfitDev, setInstantMaxProfitDev] = React.useState(rule ? String(rule.instant_max_profit_dev ?? 0) : '0');
    const [instantMaxLossDev, setInstantMaxLossDev] = React.useState(rule ? String(rule.instant_max_loss_dev ?? 0) : '0');
    const [instantMaxVolume, setInstantMaxVolume] = React.useState(rule ? String(rule.instant_max_volume ?? 0.0) : '0.0');
    const [requestTimeout, setRequestTimeout] = React.useState(rule ? String(rule.request_timeout ?? 0) : '0');
    const [requestConfirm, setRequestConfirm] = React.useState(rule?.request_confirm ?? false);
    // Margin Tab
    const [useDefaultMargin, setUseDefaultMargin] = React.useState(rule?.use_default_margin ?? true);
    const [initialMargin, setInitialMargin] = React.useState(rule ? String(rule.initial_margin ?? 0.0) : '0.0');
    const [maintenanceMargin, setMaintenanceMargin] = React.useState(rule ? String(rule.maintenance_margin ?? 0.0) : '0.0');
    const [hedgedMargin, setHedgedMargin] = React.useState(rule ? String(rule.hedged_margin ?? 0.0) : '0.0');
    const [calcHedgedLargerLeg, setCalcHedgedLargerLeg] = React.useState(rule?.calc_hedged_larger_leg ?? false);
    const [excludeLongPnl, setExcludeLongPnl] = React.useState(rule?.exclude_long_pnl ?? false);
    const [recalcMarginEod, setRecalcMarginEod] = React.useState(rule?.recalc_margin_eod ?? true);
    const [marginCheckExec, setMarginCheckExec] = React.useState(rule?.margin_check_exec ?? true);
    const [marginCheckSltp, setMarginCheckSltp] = React.useState(rule?.margin_check_sltp ?? false);
    // Margin Rates Tab
    const [useDefaultMarginRates, setUseDefaultMarginRates] = React.useState(rule?.use_default_margin_rates ?? true);
    const [liquidityRate, setLiquidityRate] = React.useState(rule ? String(rule.liquidity_rate ?? 0.0) : '0.0');
    const [currencyRate, setCurrencyRate] = React.useState(rule ? String(rule.currency_rate ?? 0.0) : '0.0');
    const [rateMarketBuy, setRateMarketBuy] = React.useState(rule ? String(rule.rate_market_buy ?? 1.0) : '1.0');
    const [rateMarketSell, setRateMarketSell] = React.useState(rule ? String(rule.rate_market_sell ?? 1.0) : '1.0');
    const [rateLimitBuy, setRateLimitBuy] = React.useState(rule ? String(rule.rate_limit_buy ?? 1.0) : '1.0');
    const [rateLimitSell, setRateLimitSell] = React.useState(rule ? String(rule.rate_limit_sell ?? 1.0) : '1.0');
    const [rateStopBuy, setRateStopBuy] = React.useState(rule ? String(rule.rate_stop_buy ?? 1.0) : '1.0');
    const [rateStopSell, setRateStopSell] = React.useState(rule ? String(rule.rate_stop_sell ?? 1.0) : '1.0');
    const [rateStopLimitBuy, setRateStopLimitBuy] = React.useState(rule ? String(rule.rate_stop_limit_buy ?? 1.0) : '1.0');
    const [rateStopLimitSell, setRateStopLimitSell] = React.useState(rule ? String(rule.rate_stop_limit_sell ?? 1.0) : '1.0');
    // Swaps Tab
    const [swapType, setSwapType] = React.useState(rule?.swap_type ?? 'disabled'); // disabled, points, percent, etc.
    const [swapLong, setSwapLong] = React.useState(rule ? String(rule.swap_long ?? 0.0) : '0.0');
    const [swapShort, setSwapShort] = React.useState(rule ? String(rule.swap_short ?? 0.0) : '0.0');
    const [swapDaysInYear, setSwapDaysInYear] = React.useState(rule?.swap_days_in_year ?? 360);
    const [swapMultMon, setSwapMultMon] = React.useState(rule ? String(rule.swap_multiplier_mon ?? 1) : '1');
    const [swapMultTue, setSwapMultTue] = React.useState(rule ? String(rule.swap_multiplier_tue ?? 1) : '1');
    const [swapMultWed, setSwapMultWed] = React.useState(rule ? String(rule.swap_multiplier_wed ?? 3) : '3');
    const [swapMultThu, setSwapMultThu] = React.useState(rule ? String(rule.swap_multiplier_thu ?? 1) : '1');
    const [swapMultFri, setSwapMultFri] = React.useState(rule ? String(rule.swap_multiplier_fri ?? 1) : '1');
    const [swapMultSat, setSwapMultSat] = React.useState(rule ? String(rule.swap_multiplier_sat ?? 0) : '0');
    const [swapMultSun, setSwapMultSun] = React.useState(rule ? String(rule.swap_multiplier_sun ?? 0) : '0');
    const [swapConsiderHolidays, setSwapConsiderHolidays] = React.useState(rule?.swap_consider_holidays ?? true);
    const [commissionRate, setCommissionRate] = React.useState(rule ? String(rule.commission_rate) : '0.0');
    const [marginRate, setMarginRate] = React.useState(rule ? String(rule.margin_rate) : '1.0');
    const handleSave = (e) => {
        e.preventDefault();
        setError(null);
        // Validation
        const trimmed = symbol.trim();
        if (!trimmed) {
            setError('Symbol pattern cannot be empty.');
            setActiveTab('common');
            return;
        }
        const parts = trimmed.split(',').map(s => s.trim()).filter(Boolean);
        if (parts.length === 0) {
            setError('Please specify at least one valid symbol or mask.');
            setActiveTab('common');
            return;
        }
        const hasPositive = parts.some(p => !p.startsWith('!'));
        if (!hasPositive) {
            setError('Rules cannot contain only exclusions (!). At least one positive mask or symbol must be defined.');
            setActiveTab('common');
            return;
        }
        onSave({
            symbol: trimmed,
            trade_allowed: useDefaultTrade ? true : (tradeMode !== 'disabled'),
            spread_diff: useDefaultSpreads ? 0 : (parseInt(spreadDiff) || 0),
            commission_rate: parseFloat(commissionRate) || 0.0,
            margin_rate: parseFloat(marginRate) || 1.0,
            // Save Tab Details
            enable_dom: enableDom,
            dom_limit: domLimit,
            use_default_spreads: useDefaultSpreads,
            diff_balance: diffBalance,
            use_default_volumes: useDefaultVolumes,
            vol_min: parseFloat(volMin) || 0.01,
            vol_step: parseFloat(volStep) || 0.01,
            vol_max: parseFloat(volMax) || 100.0,
            use_default_limit: useDefaultLimit,
            vol_limit: parseFloat(volLimit) || 0.0,
            use_default_trade: useDefaultTrade,
            trade_mode: tradeMode,
            filling_fok: fillingFok,
            filling_ioc: fillingIoc,
            filling_boc: fillingBoc,
            expiration_gtc: expirationGtc,
            expiration_day: expirationDay,
            expiration_time: expirationTime,
            expiration_date: expirationDate,
            use_default_trade_levels: useDefaultTradeLevels,
            limit_stop_level: parseInt(limitStopLevel) || 0,
            freeze_level: parseInt(freezeLevel) || 0,
            use_default_execution: useDefaultExecution,
            exec_mode: execMode,
            instant_max_time_dev: parseInt(instantMaxTimeDev) || 0,
            instant_max_profit_dev: parseInt(instantMaxProfitDev) || 0,
            instant_max_loss_dev: parseInt(instantMaxLossDev) || 0,
            instant_max_volume: parseFloat(instantMaxVolume) || 0.0,
            request_timeout: parseInt(requestTimeout) || 0,
            request_confirm: requestConfirm,
            use_default_margin: useDefaultMargin,
            initial_margin: parseFloat(initialMargin) || 0.0,
            maintenance_margin: parseFloat(maintenanceMargin) || 0.0,
            hedged_margin: parseFloat(hedgedMargin) || 0.0,
            calc_hedged_larger_leg: calcHedgedLargerLeg,
            exclude_long_pnl: excludeLongPnl,
            recalc_margin_eod: recalcMarginEod,
            margin_check_exec: marginCheckExec,
            margin_check_sltp: marginCheckSltp,
            use_default_margin_rates: useDefaultMarginRates,
            liquidity_rate: parseFloat(liquidityRate) || 0.0,
            currency_rate: parseFloat(currencyRate) || 0.0,
            rate_market_buy: parseFloat(rateMarketBuy) || 1.0,
            rate_market_sell: parseFloat(rateMarketSell) || 1.0,
            rate_limit_buy: parseFloat(rateLimitBuy) || 1.0,
            rate_limit_sell: parseFloat(rateLimitSell) || 1.0,
            rate_stop_buy: parseFloat(rateStopBuy) || 1.0,
            rate_stop_sell: parseFloat(rateStopSell) || 1.0,
            rate_stop_limit_buy: parseFloat(rateStopLimitBuy) || 1.0,
            rate_stop_limit_sell: parseFloat(rateStopLimitSell) || 1.0,
            swap_type: swapType,
            swap_long: parseFloat(swapLong) || 0.0,
            swap_short: parseFloat(swapShort) || 0.0,
            swap_days_in_year: swapDaysInYear,
            swap_multiplier_mon: parseInt(swapMultMon) || 1,
            swap_multiplier_tue: parseInt(swapMultTue) || 1,
            swap_multiplier_wed: parseInt(swapMultWed) || 3,
            swap_multiplier_thu: parseInt(swapMultThu) || 1,
            swap_multiplier_fri: parseInt(swapMultFri) || 1,
            swap_multiplier_sat: parseInt(swapMultSat) || 0,
            swap_multiplier_sun: parseInt(swapMultSun) || 0,
            swap_consider_holidays: swapConsiderHolidays
        });
        onClose();
    };
    const handleApplyForexSwaps = () => {
        setSwapMultMon('1');
        setSwapMultTue('1');
        setSwapMultWed('3');
        setSwapMultThu('1');
        setSwapMultFri('1');
        setSwapMultSat('0');
        setSwapMultSun('0');
    };
    const handleApplyAllWeekSwaps = () => {
        setSwapMultMon('1');
        setSwapMultTue('1');
        setSwapMultWed('1');
        setSwapMultThu('1');
        setSwapMultFri('1');
        setSwapMultSat('1');
        setSwapMultSun('1');
    };
    return (React.createElement("div", { className: "adm-modal-overlay", style: { zIndex: 1100 }, onClick: onClose },
        React.createElement("form", { className: "adm-modal", style: { width: 550, height: 500, display: 'flex', flexDirection: 'column' }, onClick: e => e.stopPropagation(), onSubmit: handleSave },
            React.createElement("div", { className: "adm-modal-header", style: { flexShrink: 0 } },
                React.createElement("h2", null, rule ? 'Edit Symbol Access Rule' : 'Add Symbol Access Rule'),
                React.createElement("button", { type: "button", className: "adm-modal-close", onClick: onClose }, "\u00D7")),
            React.createElement("div", { style: { display: 'flex', background: 'var(--theia-editor-background)', borderBottom: '1px solid var(--theia-border)', padding: '0 12px', gap: 8, flexShrink: 0 } }, ['common', 'trade', 'execution', 'margin', 'rates', 'swaps'].map((tab) => (React.createElement("button", { key: tab, type: "button", className: `adm-tab ${activeTab === tab ? 'active' : ''}`, onClick: () => setActiveTab(tab), style: {
                    border: 'none',
                    background: 'transparent',
                    padding: '8px 12px',
                    fontSize: 11,
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                    borderBottom: activeTab === tab ? '2px solid var(--theia-accentColor, #3498db)' : '2px solid transparent',
                    color: activeTab === tab ? 'var(--theia-foreground)' : 'var(--theia-descriptionForeground)'
                } }, tab === 'rates' ? 'Margin Rates' : tab)))),
            React.createElement("div", { className: "adm-modal-body", style: { flex: 1, overflowY: 'auto', padding: 16 } },
                error && (React.createElement("div", { className: "adm-hint", style: { background: 'var(--theia-inputValidation-errorBackground)', color: 'var(--theia-errorForeground)', margin: '0 0 12px 0' } },
                    React.createElement("i", { className: "codicon codicon-error" }),
                    " ",
                    error)),
                activeTab === 'common' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", { className: "required" }, "Symbol / Mask"),
                        React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column' } },
                            React.createElement("input", { className: "adm-input", required: true, placeholder: "e.g. * or EURUSD or !GBPUSD", value: symbol, onChange: e => setSymbol(e.target.value) }),
                            React.createElement("span", { className: "adm-field-desc" },
                                "Use ",
                                React.createElement("code", null, "*"),
                                " for wildcard, ",
                                React.createElement("code", null, "!"),
                                " to exclude (e.g. ",
                                React.createElement("code", null, "*,!BTCUSD"),
                                ")."))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Market Depth"),
                        React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column', gap: 6 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: enableDom, onChange: e => setEnableDom(e.target.checked) }),
                                React.createElement("span", null, "Enable depth of market")),
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 6 } },
                                React.createElement("span", { style: { fontSize: 11, opacity: 0.8 } }, "Depth limit:"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, value: domLimit, onChange: e => setDomLimit(e.target.value) })))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Spreads"),
                        React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column', gap: 6 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: useDefaultSpreads, onChange: e => setUseDefaultSpreads(e.target.checked) }),
                                React.createElement("span", null, "Use default spreads")),
                            !useDefaultSpreads && (React.createElement("div", { style: { display: 'flex', gap: 12 } },
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 6 } },
                                    React.createElement("span", { style: { fontSize: 11, opacity: 0.8 } }, "Spread Diff:"),
                                    React.createElement("input", { className: "adm-input", style: { width: 60 }, type: "number", value: spreadDiff, onChange: e => setSpreadDiff(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 6 } },
                                    React.createElement("span", { style: { fontSize: 11, opacity: 0.8 } }, "Balance (Bid/Ask):"),
                                    React.createElement("input", { className: "adm-input", style: { width: 80 }, value: diffBalance, onChange: e => setDiffBalance(e.target.value) })))))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Order Volumes"),
                        React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column', gap: 6 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: useDefaultVolumes, onChange: e => setUseDefaultVolumes(e.target.checked) }),
                                React.createElement("span", null, "Use default volumes")),
                            !useDefaultVolumes && (React.createElement("div", { style: { display: 'flex', gap: 8, flexWrap: 'wrap' } },
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 4 } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Min:"),
                                    React.createElement("input", { className: "adm-input", style: { width: 50 }, type: "number", step: "0.01", value: volMin, onChange: e => setVolMin(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 4 } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Step:"),
                                    React.createElement("input", { className: "adm-input", style: { width: 50 }, type: "number", step: "0.01", value: volStep, onChange: e => setVolStep(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 4 } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Max:"),
                                    React.createElement("input", { className: "adm-input", style: { width: 60 }, type: "number", step: "0.1", value: volMax, onChange: e => setVolMax(e.target.value) })))))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Position Limit"),
                        React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column', gap: 6 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: useDefaultLimit, onChange: e => setUseDefaultLimit(e.target.checked) }),
                                React.createElement("span", null, "Use default limit")),
                            !useDefaultLimit && (React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 6 } },
                                React.createElement("span", { style: { fontSize: 11, opacity: 0.8 } }, "Limit:"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, type: "number", step: "0.1", value: volLimit, onChange: e => setVolLimit(e.target.value) }),
                                React.createElement("span", { style: { fontSize: 10, opacity: 0.7 } }, "lots"))))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Commission (rate)"),
                        React.createElement("input", { className: "adm-input", type: "number", step: "0.0001", value: commissionRate, onChange: e => setCommissionRate(e.target.value) })))),
                activeTab === 'trade' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Trade Settings"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                            React.createElement("input", { type: "checkbox", checked: useDefaultTrade, onChange: e => setUseDefaultTrade(e.target.checked) }),
                            React.createElement("span", null, "Use default trade settings"))),
                    !useDefaultTrade && (React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Trade Permission"),
                        React.createElement("select", { className: "adm-input", value: tradeMode, onChange: e => setTradeMode(e.target.value) },
                            React.createElement("option", { value: "full" }, "Full Access"),
                            React.createElement("option", { value: "close" }, "Close Only"),
                            React.createElement("option", { value: "long" }, "Long Only"),
                            React.createElement("option", { value: "short" }, "Short Only"),
                            React.createElement("option", { value: "disabled" }, "Disabled")))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Filling Policies"),
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: fillingFok, onChange: e => setFillingFok(e.target.checked) }),
                                React.createElement("span", null, "Fill or Kill (FOK)")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: fillingIoc, onChange: e => setFillingIoc(e.target.checked) }),
                                React.createElement("span", null, "Immediate or Cancel (IOC)")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: fillingBoc, onChange: e => setFillingBoc(e.target.checked) }),
                                React.createElement("span", null, "Book or Cancel (BOC)")))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Expiration Mode"),
                        React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: expirationGtc, onChange: e => setExpirationGtc(e.target.checked) }),
                                React.createElement("span", null, "Good till canceled (GTC)")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: expirationDay, onChange: e => setExpirationDay(e.target.checked) }),
                                React.createElement("span", null, "Day order")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: expirationTime, onChange: e => setExpirationTime(e.target.checked) }),
                                React.createElement("span", null, "Specified time")),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: expirationDate, onChange: e => setExpirationDate(e.target.checked) }),
                                React.createElement("span", null, "Specified day")))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Trade Levels"),
                        React.createElement("div", { style: { flex: 1, display: 'flex', flexDirection: 'column', gap: 6 } },
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                React.createElement("input", { type: "checkbox", checked: useDefaultTradeLevels, onChange: e => setUseDefaultTradeLevels(e.target.checked) }),
                                React.createElement("span", null, "Use default level settings")),
                            !useDefaultTradeLevels && (React.createElement("div", { style: { display: 'flex', gap: 12 } },
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 4 } },
                                    React.createElement("span", { style: { fontSize: 11 } }, "Stops:"),
                                    React.createElement("input", { className: "adm-input", style: { width: 60 }, type: "number", value: limitStopLevel, onChange: e => setLimitStopLevel(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: 4 } },
                                    React.createElement("span", { style: { fontSize: 11 } }, "Freeze:"),
                                    React.createElement("input", { className: "adm-input", style: { width: 60 }, type: "number", value: freezeLevel, onChange: e => setFreezeLevel(e.target.value) })))))))),
                activeTab === 'execution' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Execution Settings"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                            React.createElement("input", { type: "checkbox", checked: useDefaultExecution, onChange: e => setUseDefaultExecution(e.target.checked) }),
                            React.createElement("span", null, "Use default execution settings"))),
                    !useDefaultExecution && (React.createElement(React.Fragment, null,
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Execution Mode"),
                            React.createElement("select", { className: "adm-input", value: execMode, onChange: e => setExecMode(e.target.value) },
                                React.createElement("option", { value: "instant" }, "Instant Execution"),
                                React.createElement("option", { value: "request" }, "Request Execution"),
                                React.createElement("option", { value: "market" }, "Market Execution"),
                                React.createElement("option", { value: "exchange" }, "Exchange Execution"))),
                        execMode === 'instant' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8, paddingLeft: 12, borderLeft: '2px solid var(--theia-border)' } },
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("span", { style: { width: 120, fontSize: 11 } }, "Max time dev (s):"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, type: "number", value: instantMaxTimeDev, onChange: e => setInstantMaxTimeDev(e.target.value) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("span", { style: { width: 120, fontSize: 11 } }, "Max profit dev:"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, type: "number", value: instantMaxProfitDev, onChange: e => setInstantMaxProfitDev(e.target.value) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("span", { style: { width: 120, fontSize: 11 } }, "Max losing dev:"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, type: "number", value: instantMaxLossDev, onChange: e => setInstantMaxLossDev(e.target.value) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("span", { style: { width: 120, fontSize: 11 } }, "Max volume (lots):"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, type: "number", step: "0.1", value: instantMaxVolume, onChange: e => setInstantMaxVolume(e.target.value) })))),
                        execMode === 'request' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 8, paddingLeft: 12, borderLeft: '2px solid var(--theia-border)' } },
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("span", { style: { width: 120, fontSize: 11 } }, "Timeout (s):"),
                                React.createElement("input", { className: "adm-input", style: { width: 80 }, type: "number", value: requestTimeout, onChange: e => setRequestTimeout(e.target.value) })),
                            React.createElement("div", { className: "adm-form-row" },
                                React.createElement("span", { style: { width: 120, fontSize: 11 } }, "Confirm orders:"),
                                React.createElement("input", { type: "checkbox", checked: requestConfirm, onChange: e => setRequestConfirm(e.target.checked) })))))))),
                activeTab === 'margin' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Margin Settings"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                            React.createElement("input", { type: "checkbox", checked: useDefaultMargin, onChange: e => setUseDefaultMargin(e.target.checked) }),
                            React.createElement("span", null, "Use default margin settings"))),
                    !useDefaultMargin && (React.createElement(React.Fragment, null,
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Initial Margin"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.1", value: initialMargin, onChange: e => setInitialMargin(e.target.value) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Maintenance Margin"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.1", value: maintenanceMargin, onChange: e => setMaintenanceMargin(e.target.value) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Hedged Margin"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.1", value: hedgedMargin, onChange: e => setHedgedMargin(e.target.value) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Hedged Mode"),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                                React.createElement("input", { type: "checkbox", checked: calcHedgedLargerLeg, onChange: e => setCalcHedgedLargerLeg(e.target.checked) }),
                                React.createElement("span", null, "Calculate hedged margin using larger leg"))),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Free Margin Rules"),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                                React.createElement("input", { type: "checkbox", checked: excludeLongPnl, onChange: e => setExcludeLongPnl(e.target.checked) }),
                                React.createElement("span", null, "Exclude long position PnL"))),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "End of Day"),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                                React.createElement("input", { type: "checkbox", checked: recalcMarginEod, onChange: e => setRecalcMarginEod(e.target.checked) }),
                                React.createElement("span", null, "Recalculate margin exchange rate at EOD"))),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Additional Checks"),
                            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
                                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                    React.createElement("input", { type: "checkbox", checked: marginCheckExec, onChange: e => setMarginCheckExec(e.target.checked) }),
                                    React.createElement("span", null, "Check before executing orders")),
                                React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' } },
                                    React.createElement("input", { type: "checkbox", checked: marginCheckSltp, onChange: e => setMarginCheckSltp(e.target.checked) }),
                                    React.createElement("span", null, "Check on SL-TP trigger")))))),
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Margin Multiplier"),
                        React.createElement("input", { className: "adm-input", type: "number", step: "0.1", value: marginRate, onChange: e => setMarginRate(e.target.value) })))),
                activeTab === 'rates' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Margin Rates"),
                        React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                            React.createElement("input", { type: "checkbox", checked: useDefaultMarginRates, onChange: e => setUseDefaultMarginRates(e.target.checked) }),
                            React.createElement("span", null, "Use default margin rate settings"))),
                    !useDefaultMarginRates && (React.createElement(React.Fragment, null,
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Liquidity Rate"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.1", value: liquidityRate, onChange: e => setLiquidityRate(e.target.value) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Currency Rate"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.1", value: currencyRate, onChange: e => setCurrencyRate(e.target.value) })),
                        React.createElement("div", { style: { background: 'var(--theia-sideBarSectionHeader-background)', padding: 8, borderRadius: 4 } },
                            React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, fontWeight: 'bold', fontSize: 10, borderBottom: '1px solid var(--theia-border)', paddingBottom: 4, marginBottom: 6 } },
                                React.createElement("span", null, "Order Type"),
                                React.createElement("span", null, "Initial"),
                                React.createElement("span", null, "Maintenance")),
                            React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 6 } },
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Market Buy"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateMarketBuy, onChange: e => setRateMarketBuy(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Market Sell"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateMarketSell, onChange: e => setRateMarketSell(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Buy Limit"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateLimitBuy, onChange: e => setRateLimitBuy(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Sell Limit"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateLimitSell, onChange: e => setRateLimitSell(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Buy Stop"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateStopBuy, onChange: e => setRateStopBuy(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Sell Stop"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateStopSell, onChange: e => setRateStopSell(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Buy Stop Limit"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateStopLimitBuy, onChange: e => setRateStopLimitBuy(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")),
                                React.createElement("div", { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, alignItems: 'center' } },
                                    React.createElement("span", { style: { fontSize: 10 } }, "Sell Stop Limit"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", step: "0.1", value: rateStopLimitSell, onChange: e => setRateStopLimitSell(e.target.value) }),
                                    React.createElement("span", { style: { fontSize: 9, opacity: 0.7 } }, "Same")))))))),
                activeTab === 'swaps' && (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 10 } },
                    React.createElement("div", { className: "adm-form-row" },
                        React.createElement("label", null, "Swap Type"),
                        React.createElement("select", { className: "adm-input", value: swapType, onChange: e => setSwapType(e.target.value) },
                            React.createElement("option", { value: "disabled" }, "Disabled"),
                            React.createElement("option", { value: "points" }, "Points"),
                            React.createElement("option", { value: "percent" }, "Percentage"),
                            React.createElement("option", { value: "interest" }, "Interest Rate"))),
                    swapType !== 'disabled' && (React.createElement(React.Fragment, null,
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Long Positions"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.01", value: swapLong, onChange: e => setSwapLong(e.target.value) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Short Positions"),
                            React.createElement("input", { className: "adm-input", type: "number", step: "0.01", value: swapShort, onChange: e => setSwapShort(e.target.value) })),
                        React.createElement("div", { className: "adm-form-row" },
                            React.createElement("label", null, "Days in Year"),
                            React.createElement("select", { className: "adm-input", value: swapDaysInYear, onChange: e => setSwapDaysInYear(parseInt(e.target.value)) },
                                React.createElement("option", { value: 360 }, "360 days"),
                                React.createElement("option", { value: 365 }, "365 days"),
                                React.createElement("option", { value: 366 }, "366 days"))),
                        React.createElement("div", { style: { background: 'var(--theia-sideBarSectionHeader-background)', padding: 8, borderRadius: 4 } },
                            React.createElement("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--theia-border)', paddingBottom: 4, marginBottom: 8 } },
                                React.createElement("span", { style: { fontWeight: 'bold', fontSize: 10 } }, "Swap Multipliers"),
                                React.createElement("div", { style: { display: 'flex', gap: 4 } },
                                    React.createElement("button", { type: "button", className: "adm-btn", style: { fontSize: 9, padding: '1px 4px', height: 16 }, onClick: handleApplyForexSwaps }, "Forex"),
                                    React.createElement("button", { type: "button", className: "adm-btn", style: { fontSize: 9, padding: '1px 4px', height: 16 }, onClick: handleApplyAllWeekSwaps }, "All Week"))),
                            React.createElement("div", { style: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6 } },
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Mon"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultMon, onChange: e => setSwapMultMon(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Tue"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultTue, onChange: e => setSwapMultTue(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Wed"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultWed, onChange: e => setSwapMultWed(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Thu"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultThu, onChange: e => setSwapMultThu(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Fri"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultFri, onChange: e => setSwapMultFri(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Sat"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultSat, onChange: e => setSwapMultSat(e.target.value) })),
                                React.createElement("div", { style: { display: 'flex', flexDirection: 'column', gap: 2 } },
                                    React.createElement("span", { style: { fontSize: 9 } }, "Sun"),
                                    React.createElement("input", { className: "adm-input", style: { height: 18, fontSize: 10 }, type: "number", value: swapMultSun, onChange: e => setSwapMultSun(e.target.value) })))),
                        React.createElement("div", { className: "adm-form-row", style: { marginTop: 8 } },
                            React.createElement("label", null, "Holidays"),
                            React.createElement("label", { style: { display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', flex: 1 } },
                                React.createElement("input", { type: "checkbox", checked: swapConsiderHolidays, onChange: e => setSwapConsiderHolidays(e.target.checked) }),
                                React.createElement("span", null, "Consider holidays in swap charging")))))))),
            React.createElement("div", { className: "adm-modal-footer", style: { flexShrink: 0 } },
                React.createElement("button", { type: "submit", className: "adm-btn adm-btn-primary" }, "Save Rule"),
                React.createElement("button", { type: "button", className: "adm-btn", onClick: onClose }, "Cancel")))));
}
exports.SymbolRuleDialog = SymbolRuleDialog;
//# sourceMappingURL=SymbolRuleDialog.js.map