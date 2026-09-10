# 📁 Platform-Components

- **Generated:** 2026-09-10 12:32
- **Total Files:** 119
- **Source:** `C:\Users\DELL\Desktop\New folder (2)\MT5-Administrator\MetaTrader5Administrator\MetaTrader-5-Trading-Platform\Platform-Components`

---

## 📑 Table of Contents

1. [Access-Server.md](#access-server-md)
2. [Backup-Server.md](#backup-server-md)
3. [Data-Feeds.md](#data-feeds-md)
4. [Gateways.md](#gateways-md)
5. [History-Server.md](#history-server-md)
6. [Old-WebTerminal.md](#old-webterminal-md)
7. [Trade-Server.md](#trade-server-md)
8. [WebTerminal.md](#webterminal-md)
9. [Access-Server/Antiflood-Control.md](#access-server-antiflood-control-md)
10. [Access-Server/Priority.md](#access-server-priority-md)
11. [Access-Server/Structure-of-Directories-and-Files.md](#access-server-structure-of-directories-and-files-md)
12. [Backup-Server/Backup-Features.md](#backup-server-backup-features-md)
13. [Backup-Server/Restoring-Server.md](#backup-server-restoring-server-md)
14. [Backup-Server/SQL-Export.md](#backup-server-sql-export-md)
15. [Backup-Server/Switching-to.md](#backup-server-switching-to-md)
16. [Backup-Server/SQL-Export/Installation-and-Setup-of-MS-SQL.md](#backup-server-sql-export-installation-and-setup-of-ms-sql-md)
17. [Backup-Server/SQL-Export/Installation-and-Setup-of-MariaDB.md](#backup-server-sql-export-installation-and-setup-of-mariadb-md)
18. [Backup-Server/SQL-Export/Installation-and-Setup-of-MySQL.md](#backup-server-sql-export-installation-and-setup-of-mysql-md)
19. [Backup-Server/SQL-Export/Installation-and-Setup-of-Oracle.md](#backup-server-sql-export-installation-and-setup-of-oracle-md)
20. [Backup-Server/SQL-Export/Installation-and-Setup-of-PostgreSQL.md](#backup-server-sql-export-installation-and-setup-of-postgresql-md)
21. [Backup-Server/SQL-Export/mt5-accounts.md](#backup-server-sql-export-mt5-accounts-md)
22. [Backup-Server/SQL-Export/mt5-clients.md](#backup-server-sql-export-mt5-clients-md)
23. [Backup-Server/SQL-Export/mt5-commissions-tiers.md](#backup-server-sql-export-mt5-commissions-tiers-md)
24. [Backup-Server/SQL-Export/mt5-commissions.md](#backup-server-sql-export-mt5-commissions-md)
25. [Backup-Server/SQL-Export/mt5-daily-orders.md](#backup-server-sql-export-mt5-daily-orders-md)
26. [Backup-Server/SQL-Export/mt5-daily-positions.md](#backup-server-sql-export-mt5-daily-positions-md)
27. [Backup-Server/SQL-Export/mt5-daily.md](#backup-server-sql-export-mt5-daily-md)
28. [Backup-Server/SQL-Export/mt5-deals.md](#backup-server-sql-export-mt5-deals-md)
29. [Backup-Server/SQL-Export/mt5-documents.md](#backup-server-sql-export-mt5-documents-md)
30. [Backup-Server/SQL-Export/mt5-feeder-params.md](#backup-server-sql-export-mt5-feeder-params-md)
31. [Backup-Server/SQL-Export/mt5-feeder-symbols.md](#backup-server-sql-export-mt5-feeder-symbols-md)
32. [Backup-Server/SQL-Export/mt5-feeder-translates.md](#backup-server-sql-export-mt5-feeder-translates-md)
33. [Backup-Server/SQL-Export/mt5-feeders.md](#backup-server-sql-export-mt5-feeders-md)
34. [Backup-Server/SQL-Export/mt5-firewall.md](#backup-server-sql-export-mt5-firewall-md)
35. [Backup-Server/SQL-Export/mt5-gateways-params.md](#backup-server-sql-export-mt5-gateways-params-md)
36. [Backup-Server/SQL-Export/mt5-gateways-symbols.md](#backup-server-sql-export-mt5-gateways-symbols-md)
37. [Backup-Server/SQL-Export/mt5-gateways-translates.md](#backup-server-sql-export-mt5-gateways-translates-md)
38. [Backup-Server/SQL-Export/mt5-gateways.md](#backup-server-sql-export-mt5-gateways-md)
39. [Backup-Server/SQL-Export/mt5-groups-symbols.md](#backup-server-sql-export-mt5-groups-symbols-md)
40. [Backup-Server/SQL-Export/mt5-groups.md](#backup-server-sql-export-mt5-groups-md)
41. [Backup-Server/SQL-Export/mt5-holidays.md](#backup-server-sql-export-mt5-holidays-md)
42. [Backup-Server/SQL-Export/mt5-managers.md](#backup-server-sql-export-mt5-managers-md)
43. [Backup-Server/SQL-Export/mt5-network-access-servers.md](#backup-server-sql-export-mt5-network-access-servers-md)
44. [Backup-Server/SQL-Export/mt5-network-backup-folders.md](#backup-server-sql-export-mt5-network-backup-folders-md)
45. [Backup-Server/SQL-Export/mt5-network-backup-servers.md](#backup-server-sql-export-mt5-network-backup-servers-md)
46. [Backup-Server/SQL-Export/mt5-network-history-servers.md](#backup-server-sql-export-mt5-network-history-servers-md)
47. [Backup-Server/SQL-Export/mt5-network-trade-servers.md](#backup-server-sql-export-mt5-network-trade-servers-md)
48. [Backup-Server/SQL-Export/mt5-network.md](#backup-server-sql-export-mt5-network-md)
49. [Backup-Server/SQL-Export/mt5-orders-history.md](#backup-server-sql-export-mt5-orders-history-md)
50. [Backup-Server/SQL-Export/mt5-orders.md](#backup-server-sql-export-mt5-orders-md)
51. [Backup-Server/SQL-Export/mt5-plugin-params.md](#backup-server-sql-export-mt5-plugin-params-md)
52. [Backup-Server/SQL-Export/mt5-plugins.md](#backup-server-sql-export-mt5-plugins-md)
53. [Backup-Server/SQL-Export/mt5-positions.md](#backup-server-sql-export-mt5-positions-md)
54. [Backup-Server/SQL-Export/mt5-prices.md](#backup-server-sql-export-mt5-prices-md)
55. [Backup-Server/SQL-Export/mt5-report-params.md](#backup-server-sql-export-mt5-report-params-md)
56. [Backup-Server/SQL-Export/mt5-reports.md](#backup-server-sql-export-mt5-reports-md)
57. [Backup-Server/SQL-Export/mt5-routing-conds.md](#backup-server-sql-export-mt5-routing-conds-md)
58. [Backup-Server/SQL-Export/mt5-routing-dealers.md](#backup-server-sql-export-mt5-routing-dealers-md)
59. [Backup-Server/SQL-Export/mt5-routing.md](#backup-server-sql-export-mt5-routing-md)
60. [Backup-Server/SQL-Export/mt5-symbols-sessions.md](#backup-server-sql-export-mt5-symbols-sessions-md)
61. [Backup-Server/SQL-Export/mt5-symbols.md](#backup-server-sql-export-mt5-symbols-md)
62. [Backup-Server/SQL-Export/mt5-time-weekdays.md](#backup-server-sql-export-mt5-time-weekdays-md)
63. [Backup-Server/SQL-Export/mt5-time.md](#backup-server-sql-export-mt5-time-md)
64. [Backup-Server/SQL-Export/mt5-users.md](#backup-server-sql-export-mt5-users-md)
65. [Backup-Server/SQL-Export/mt5-deals/Enumerations.md](#backup-server-sql-export-mt5-deals-enumerations-md)
66. [Backup-Server/SQL-Export/mt5-feeders/Enumerations.md](#backup-server-sql-export-mt5-feeders-enumerations-md)
67. [Backup-Server/SQL-Export/mt5-groups/Enumerations.md](#backup-server-sql-export-mt5-groups-enumerations-md)
68. [Backup-Server/SQL-Export/mt5-orders/Enumerations.md](#backup-server-sql-export-mt5-orders-enumerations-md)
69. [Backup-Server/SQL-Export/mt5-positions/Enumerations.md](#backup-server-sql-export-mt5-positions-enumerations-md)
70. [Backup-Server/SQL-Export/mt5-routing/Enumerations.md](#backup-server-sql-export-mt5-routing-enumerations-md)
71. [Backup-Server/SQL-Export/mt5-symbols/Enumerations.md](#backup-server-sql-export-mt5-symbols-enumerations-md)
72. [Backup-Server/SQL-Export/mt5-users/Enumerations.md](#backup-server-sql-export-mt5-users-enumerations-md)
73. [Data-Feeds/Alliance-News-Feeder.md](#data-feeds-alliance-news-feeder-md)
74. [Data-Feeds/Claws-&-Horns-Feeder.md](#data-feeds-claws-horns-feeder-md)
75. [Data-Feeds/DJ-News-Feeder.md](#data-feeds-dj-news-feeder-md)
76. [Data-Feeds/Dow-Jones-Prime-Tass-News-Feeder.md](#data-feeds-dow-jones-prime-tass-news-feeder-md)
77. [Data-Feeds/FXstreet-Feeder.md](#data-feeds-fxstreet-feeder-md)
78. [Data-Feeds/Financial-Source-News-Feeder.md](#data-feeds-financial-source-news-feeder-md)
79. [Data-Feeds/ForexPros-Feeder.md](#data-feeds-forexpros-feeder-md)
80. [Data-Feeds/IBTimes-News-Feeder.md](#data-feeds-ibtimes-news-feeder-md)
81. [Data-Feeds/IQFeeder.md](#data-feeds-iqfeeder-md)
82. [Data-Feeds/KnowledgeView-News-Feeder.md](#data-feeds-knowledgeview-news-feeder-md)
83. [Data-Feeds/MetaTrader-4-Feeder.md](#data-feeds-metatrader-4-feeder-md)
84. [Data-Feeds/MetaTrader-5-Feeder.md](#data-feeds-metatrader-5-feeder-md)
85. [Data-Feeds/MetaTrader-5-UniFeeder.md](#data-feeds-metatrader-5-unifeeder-md)
86. [Data-Feeds/Newsquawk.md](#data-feeds-newsquawk-md)
87. [Data-Feeds/RSS-News-Feeder.md](#data-feeds-rss-news-feeder-md)
88. [Data-Feeds/Remote-Datafeed.md](#data-feeds-remote-datafeed-md)
89. [Data-Feeds/Thomson-Reuters-Feeder.md](#data-feeds-thomson-reuters-feeder-md)
90. [Data-Feeds/Trading-Central-News-Feeder.md](#data-feeds-trading-central-news-feeder-md)
91. [Data-Feeds/UniNewsFeeder.md](#data-feeds-uninewsfeeder-md)
92. [Data-Feeds/Universal-DDE-Connector.md](#data-feeds-universal-dde-connector-md)
93. [Data-Feeds/Universal-DDE-Connector/Filtration-of-Quotes.md](#data-feeds-universal-dde-connector-filtration-of-quotes-md)
94. [Data-Feeds/Universal-DDE-Connector/Installation-and-Setup.md](#data-feeds-universal-dde-connector-installation-and-setup-md)
95. [Data-Feeds/Universal-DDE-Connector/Setting-Up-Symbols.md](#data-feeds-universal-dde-connector-setting-up-symbols-md)
96. [Data-Feeds/Universal-DDE-Connector/UniFeeder-Protocol.md](#data-feeds-universal-dde-connector-unifeeder-protocol-md)
97. [Gateways/Borsa-Istanbul.md](#gateways-borsa-istanbul-md)
98. [Gateways/Cboe-FX.md](#gateways-cboe-fx-md)
99. [Gateways/Currenex.md](#gateways-currenex-md)
100. [Gateways/DGCX.md](#gateways-dgcx-md)
101. [Gateways/Euronext-FX.md](#gateways-euronext-fx-md)
102. [Gateways/FXCM-PRO.md](#gateways-fxcm-pro-md)
103. [Gateways/Integral.md](#gateways-integral-md)
104. [Gateways/Interactive-Brokers.md](#gateways-interactive-brokers-md)
105. [Gateways/LMAX-Global.md](#gateways-lmax-global-md)
106. [Gateways/MOEX-Derivatives.md](#gateways-moex-derivatives-md)
107. [Gateways/MOEX-Securities.md](#gateways-moex-securities-md)
108. [Gateways/MOEXFX.md](#gateways-moexfx-md)
109. [Gateways/MetaTrader-4.md](#gateways-metatrader-4-md)
110. [Gateways/MetaTrader-5.md](#gateways-metatrader-5-md)
111. [History-Server/Console-Commands.md](#history-server-console-commands-md)
112. [History-Server/Interaction-with-Quote-Providers.md](#history-server-interaction-with-quote-providers-md)
113. [History-Server/Quotes-Filtration.md](#history-server-quotes-filtration-md)
114. [History-Server/Structure-of-Directories-and-Files.md](#history-server-structure-of-directories-and-files-md)
115. [Trade-Server/Daily-Reports.md](#trade-server-daily-reports-md)
116. [Trade-Server/Mail-Templates.md](#trade-server-mail-templates-md)
117. [Trade-Server/Return-Errors.md](#trade-server-return-errors-md)
118. [Trade-Server/SendMail-Utility.md](#trade-server-sendmail-utility-md)
119. [Trade-Server/Structure-of-Directories-and-Files.md](#trade-server-structure-of-directories-and-files-md)

---

## 🌲 Project Structure

```
Platform-Components/
├── Access-Server/
│   ├── Antiflood-Control.md
│   ├── images/
│   │   ├── access_server_preference.png
│   │   ├── network_add_access.png
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_2.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   └── previous_2.png
│   ├── Priority.md
│   └── Structure-of-Directories-and-Files.md
├── Access-Server.md
├── Backup-Server/
│   ├── Backup-Features.md
│   ├── images/
│   │   ├── backup_base_increment.png
│   │   ├── backup_base_increment_merge_1.png
│   │   ├── backup_base_increment_merge_2.png
│   │   ├── backup_restore_base.png
│   │   ├── backup_restore_increment.png
│   │   ├── backup_server_backuping_icon.png
│   │   ├── backup_server_backuping_icon2.png
│   │   ├── backup_server_gui.png
│   │   ├── network_add_access.png
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_2.png
│   │   ├── next_3.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   ├── previous_2.png
│   │   ├── previous_3.png
│   │   ├── restore_history_server.png
│   │   ├── restore_main_server.png
│   │   ├── switch_to_backup_confirm.png
│   │   ├── switch_to_backup_server_change.png
│   │   ├── switch_to_bakcup_icon.png
│   │   ├── switching_to_backup.png
│   │   └── trade_backup_settings.png
│   ├── Restoring-Server.md
│   ├── SQL-Export/
│   │   ├── images/
│   │   │   ├── mariadb_create_db.png
│   │   │   ├── mariadb_install.gif
│   │   │   ├── mariadb_install2.gif
│   │   │   ├── mariadb_setting_local.png
│   │   │   ├── mariadb_setting_remote.png
│   │   │   ├── mssql_6_a.png
│   │   │   ├── mssql_8_a.png
│   │   │   ├── mssql_aa.png
│   │   │   ├── mssql_ba.png
│   │   │   ├── mssql_tcp.png
│   │   │   ├── mysql_8.png
│   │   │   ├── mysql_configure.gif
│   │   │   ├── mysql_configure_finish.gif
│   │   │   ├── mysql_configure_users.png
│   │   │   ├── mysql_install.gif
│   │   │   ├── mysql_platform_local.png
│   │   │   ├── mysql_platform_remote.png
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_10.png
│   │   │   ├── next_11.png
│   │   │   ├── next_12.png
│   │   │   ├── next_13.png
│   │   │   ├── next_14.png
│   │   │   ├── next_15.png
│   │   │   ├── next_16.png
│   │   │   ├── next_17.png
│   │   │   ├── next_18.png
│   │   │   ├── next_19.png
│   │   │   ├── next_2.png
│   │   │   ├── next_20.png
│   │   │   ├── next_21.png
│   │   │   ├── next_22.png
│   │   │   ├── next_23.png
│   │   │   ├── next_24.png
│   │   │   ├── next_25.png
│   │   │   ├── next_26.png
│   │   │   ├── next_27.png
│   │   │   ├── next_28.png
│   │   │   ├── next_29.png
│   │   │   ├── next_3.png
│   │   │   ├── next_30.png
│   │   │   ├── next_31.png
│   │   │   ├── next_32.png
│   │   │   ├── next_33.png
│   │   │   ├── next_34.png
│   │   │   ├── next_35.png
│   │   │   ├── next_36.png
│   │   │   ├── next_37.png
│   │   │   ├── next_38.png
│   │   │   ├── next_39.png
│   │   │   ├── next_4.png
│   │   │   ├── next_40.png
│   │   │   ├── next_41.png
│   │   │   ├── next_42.png
│   │   │   ├── next_43.png
│   │   │   ├── next_44.png
│   │   │   ├── next_45.png
│   │   │   ├── next_46.png
│   │   │   ├── next_47.png
│   │   │   ├── next_48.png
│   │   │   ├── next_5.png
│   │   │   ├── next_6.png
│   │   │   ├── next_7.png
│   │   │   ├── next_8.png
│   │   │   ├── next_9.png
│   │   │   ├── oracle_4.png
│   │   │   ├── oracle_setting_local.png
│   │   │   ├── oracle_setting_remote.png
│   │   │   ├── postgre1.gif
│   │   │   ├── postgre2.gif
│   │   │   ├── postgre3.gif
│   │   │   ├── postgre_db_create.png
│   │   │   ├── postgres_settings_local.png
│   │   │   ├── postgres_settings_remote.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_10.png
│   │   │   ├── previous_11.png
│   │   │   ├── previous_12.png
│   │   │   ├── previous_13.png
│   │   │   ├── previous_14.png
│   │   │   ├── previous_15.png
│   │   │   ├── previous_16.png
│   │   │   ├── previous_17.png
│   │   │   ├── previous_18.png
│   │   │   ├── previous_19.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_20.png
│   │   │   ├── previous_21.png
│   │   │   ├── previous_22.png
│   │   │   ├── previous_23.png
│   │   │   ├── previous_24.png
│   │   │   ├── previous_25.png
│   │   │   ├── previous_26.png
│   │   │   ├── previous_27.png
│   │   │   ├── previous_28.png
│   │   │   ├── previous_29.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_30.png
│   │   │   ├── previous_31.png
│   │   │   ├── previous_32.png
│   │   │   ├── previous_33.png
│   │   │   ├── previous_34.png
│   │   │   ├── previous_35.png
│   │   │   ├── previous_36.png
│   │   │   ├── previous_37.png
│   │   │   ├── previous_38.png
│   │   │   ├── previous_39.png
│   │   │   ├── previous_4.png
│   │   │   ├── previous_40.png
│   │   │   ├── previous_41.png
│   │   │   ├── previous_42.png
│   │   │   ├── previous_43.png
│   │   │   ├── previous_44.png
│   │   │   ├── previous_45.png
│   │   │   ├── previous_46.png
│   │   │   ├── previous_47.png
│   │   │   ├── previous_48.png
│   │   │   ├── previous_5.png
│   │   │   ├── previous_6.png
│   │   │   ├── previous_7.png
│   │   │   ├── previous_8.png
│   │   │   └── previous_9.png
│   │   ├── Installation-and-Setup-of-MariaDB.md
│   │   ├── Installation-and-Setup-of-MS-SQL.md
│   │   ├── Installation-and-Setup-of-MySQL.md
│   │   ├── Installation-and-Setup-of-Oracle.md
│   │   ├── Installation-and-Setup-of-PostgreSQL.md
│   │   ├── mt5-accounts.md
│   │   ├── mt5-clients.md
│   │   ├── mt5-commissions-tiers.md
│   │   ├── mt5-commissions.md
│   │   ├── mt5-daily-orders.md
│   │   ├── mt5-daily-positions.md
│   │   ├── mt5-daily.md
│   │   ├── mt5-deals/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-deals.md
│   │   ├── mt5-documents.md
│   │   ├── mt5-feeder-params.md
│   │   ├── mt5-feeder-symbols.md
│   │   ├── mt5-feeder-translates.md
│   │   ├── mt5-feeders/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-feeders.md
│   │   ├── mt5-firewall.md
│   │   ├── mt5-gateways-params.md
│   │   ├── mt5-gateways-symbols.md
│   │   ├── mt5-gateways-translates.md
│   │   ├── mt5-gateways.md
│   │   ├── mt5-groups/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-groups-symbols.md
│   │   ├── mt5-groups.md
│   │   ├── mt5-holidays.md
│   │   ├── mt5-managers.md
│   │   ├── mt5-network-access-servers.md
│   │   ├── mt5-network-backup-folders.md
│   │   ├── mt5-network-backup-servers.md
│   │   ├── mt5-network-history-servers.md
│   │   ├── mt5-network-trade-servers.md
│   │   ├── mt5-network.md
│   │   ├── mt5-orders/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-orders-history.md
│   │   ├── mt5-orders.md
│   │   ├── mt5-plugin-params.md
│   │   ├── mt5-plugins.md
│   │   ├── mt5-positions/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-positions.md
│   │   ├── mt5-prices.md
│   │   ├── mt5-report-params.md
│   │   ├── mt5-reports.md
│   │   ├── mt5-routing/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-routing-conds.md
│   │   ├── mt5-routing-dealers.md
│   │   ├── mt5-routing.md
│   │   ├── mt5-symbols/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   ├── mt5-symbols-sessions.md
│   │   ├── mt5-symbols.md
│   │   ├── mt5-time-weekdays.md
│   │   ├── mt5-time.md
│   │   ├── mt5-users/
│   │   │   ├── Enumerations.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       └── previous.png
│   │   └── mt5-users.md
│   ├── SQL-Export.md
│   └── Switching-to.md
├── Backup-Server.md
├── Data-Feeds/
│   ├── Alliance-News-Feeder.md
│   ├── Claws-&-Horns-Feeder.md
│   ├── DJ-News-Feeder.md
│   ├── Dow-Jones-Prime-Tass-News-Feeder.md
│   ├── Financial-Source-News-Feeder.md
│   ├── ForexPros-Feeder.md
│   ├── FXstreet-Feeder.md
│   ├── IBTimes-News-Feeder.md
│   ├── images/
│   │   ├── clawshorns_common.png
│   │   ├── clawshorns_param.png
│   │   ├── data_feed_alliance_parameters.png
│   │   ├── data_feed_alliance_server.png
│   │   ├── data_feed_forexpros_parameters.png
│   │   ├── data_feed_forexpros_server.png
│   │   ├── data_feed_mt4_common.png
│   │   ├── data_feed_mt4_parameters.png
│   │   ├── data_feed_newsquawk.png
│   │   ├── data_feeds_parameters_dj.png
│   │   ├── data_feeds_parameters_dj_prime.png
│   │   ├── data_feeds_parameters_fxstreet.png
│   │   ├── data_feeds_parameters_iq.png
│   │   ├── data_feeds_parameters_kw.png
│   │   ├── data_feeds_parameters_mt5.png
│   │   ├── data_feeds_parameters_rss.png
│   │   ├── data_feeds_parameters_tcn.png
│   │   ├── data_feeds_parameters_tr.png
│   │   ├── data_feeds_parameters_uni.png
│   │   ├── data_feeds_server_dj.png
│   │   ├── data_feeds_server_dj_prime.png
│   │   ├── data_feeds_server_fxstreet.png
│   │   ├── data_feeds_server_ibt.png
│   │   ├── data_feeds_server_iq.png
│   │   ├── data_feeds_server_kw.png
│   │   ├── data_feeds_server_mt5.png
│   │   ├── data_feeds_server_rss.png
│   │   ├── data_feeds_server_tc.png
│   │   ├── data_feeds_server_tr.png
│   │   ├── data_feeds_server_uni.png
│   │   ├── financialsource_common.png
│   │   ├── forexsource_param.png
│   │   ├── iq_feed_symbol_dom.png
│   │   ├── iq_feed_symbols.png
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_10.png
│   │   ├── next_11.png
│   │   ├── next_12.png
│   │   ├── next_13.png
│   │   ├── next_14.png
│   │   ├── next_15.png
│   │   ├── next_16.png
│   │   ├── next_17.png
│   │   ├── next_18.png
│   │   ├── next_19.png
│   │   ├── next_2.png
│   │   ├── next_3.png
│   │   ├── next_4.png
│   │   ├── next_5.png
│   │   ├── next_6.png
│   │   ├── next_7.png
│   │   ├── next_8.png
│   │   ├── next_9.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   ├── previous_10.png
│   │   ├── previous_11.png
│   │   ├── previous_12.png
│   │   ├── previous_13.png
│   │   ├── previous_14.png
│   │   ├── previous_15.png
│   │   ├── previous_16.png
│   │   ├── previous_17.png
│   │   ├── previous_18.png
│   │   ├── previous_19.png
│   │   ├── previous_2.png
│   │   ├── previous_3.png
│   │   ├── previous_4.png
│   │   ├── previous_5.png
│   │   ├── previous_6.png
│   │   ├── previous_7.png
│   │   ├── previous_8.png
│   │   ├── previous_9.png
│   │   ├── remote_gateway.png
│   │   ├── uninewsfeeder_common.png
│   │   └── uninewsfeeder_param.png
│   ├── IQFeeder.md
│   ├── KnowledgeView-News-Feeder.md
│   ├── MetaTrader-4-Feeder.md
│   ├── MetaTrader-5-Feeder.md
│   ├── MetaTrader-5-UniFeeder.md
│   ├── Newsquawk.md
│   ├── Remote-Datafeed.md
│   ├── RSS-News-Feeder.md
│   ├── Thomson-Reuters-Feeder.md
│   ├── Trading-Central-News-Feeder.md
│   ├── UniNewsFeeder.md
│   ├── Universal-DDE-Connector/
│   │   ├── Filtration-of-Quotes.md
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── unidde.png
│   │   │   ├── unidde_accounts.png
│   │   │   ├── unidde_symbol.png
│   │   │   └── unidde_templates.png
│   │   ├── Installation-and-Setup.md
│   │   ├── Setting-Up-Symbols.md
│   │   └── UniFeeder-Protocol.md
│   └── Universal-DDE-Connector.md
├── Data-Feeds.md
├── Gateways/
│   ├── Borsa-Istanbul.md
│   ├── Cboe-FX.md
│   ├── Currenex.md
│   ├── DGCX.md
│   ├── Euronext-FX.md
│   ├── FXCM-PRO.md
│   ├── images/
│   │   ├── borsa_account.png
│   │   ├── borsa_common.png
│   │   ├── borsa_group_common.png
│   │   ├── borsa_groups_symbols.png
│   │   ├── borsa_margin.png
│   │   ├── borsa_param.png
│   │   ├── borsa_routing.png
│   │   ├── borsa_scheme.png
│   │   ├── coverage_account.png
│   │   ├── coverage_group.png
│   │   ├── coverage_routing.png
│   │   ├── currenex_account.png
│   │   ├── currenex_common.png
│   │   ├── currenex_groups.png
│   │   ├── currenex_margin.png
│   │   ├── currenex_param.png
│   │   ├── currenex_routing.png
│   │   ├── currenex_symbols.png
│   │   ├── currenex_translation.png
│   │   ├── dgcx_common.png
│   │   ├── dgcx_groups.png
│   │   ├── dgcx_param.png
│   │   ├── dgcx_routing_common.png
│   │   ├── dgcx_routing_dealer.png
│   │   ├── dgcx_scheme.png
│   │   ├── dgcx_swap.png
│   │   ├── dgcx_symbols.png
│   │   ├── fastmatch_account.png
│   │   ├── fastmatch_common.png
│   │   ├── fastmatch_groups.png
│   │   ├── fastmatch_margin.png
│   │   ├── fastmatch_param.png
│   │   ├── fastmatch_routing.png
│   │   ├── fastmatch_scheme.png
│   │   ├── fastmatch_symbols.png
│   │   ├── fastmatch_translation.png
│   │   ├── fxcm_account.png
│   │   ├── fxcm_common.png
│   │   ├── fxcm_groups_symbols.png
│   │   ├── fxcm_param.png
│   │   ├── fxcm_routing.png
│   │   ├── fxcm_scheme.png
│   │   ├── fxcm_translation.png
│   │   ├── hotspot_common.png
│   │   ├── hotspot_groups.png
│   │   ├── hotspot_param.png
│   │   ├── hotspot_routing.png
│   │   ├── hotspot_symbols.png
│   │   ├── hotspot_translations.png
│   │   ├── ib_gateway_accounts.png
│   │   ├── ib_gateway_accounts_1.png
│   │   ├── ib_gateway_flex_report3.png
│   │   ├── ib_gateway_flex_report_columns.png
│   │   ├── ib_gateway_flex_report_confirm.png
│   │   ├── ib_gateway_flex_report_create.png
│   │   ├── ib_gateway_flex_report_delivery.png
│   │   ├── ib_gateway_flex_report_edit.png
│   │   ├── ib_gateway_flex_report_general.png
│   │   ├── ib_gateway_flex_report_id.png
│   │   ├── ib_gateway_flex_report_query_add.png
│   │   ├── ib_gateway_flex_report_tax_docs.png
│   │   ├── ib_gateway_flex_token.png
│   │   ├── ib_gateway_flex_token2.png
│   │   ├── ib_gateway_flex_token3.png
│   │   ├── ib_gateway_groups.png
│   │   ├── ib_gateway_ibgateway_port.png
│   │   ├── ib_gateway_marketdata.png
│   │   ├── ib_gateway_multiple_login.png
│   │   ├── ib_gateway_multiple_param.png
│   │   ├── ib_gateway_param_import.png
│   │   ├── ib_gateway_param_local.png
│   │   ├── ib_gateway_proxy.png
│   │   ├── ib_gateway_routing.png
│   │   ├── ib_gateway_search_exchange.png
│   │   ├── ib_gateway_search_exchange2.png
│   │   ├── ib_gateway_symbols.png
│   │   ├── ib_gateway_symbols_1.png
│   │   ├── ib_gateway_symbols_2.png
│   │   ├── ib_gateway_twostep_disable-login.png
│   │   ├── ib_gateway_twostep_disable.png
│   │   ├── ib_gateway_tws_port.png
│   │   ├── integral_common.png
│   │   ├── integral_group.png
│   │   ├── integral_margin_allorders.png
│   │   ├── integral_margin_allorders_1.png
│   │   ├── integral_margin_allorders_2.png
│   │   ├── integral_param.png
│   │   ├── integral_routing.png
│   │   ├── integral_scheme.png
│   │   ├── integral_symbols.png
│   │   ├── integral_tranlsation.png
│   │   ├── lmax_common.png
│   │   ├── lmax_groups_symbols.png
│   │   ├── lmax_param.png
│   │   ├── lmax_routing.png
│   │   ├── lmax_scheme.png
│   │   ├── lmax_translation.png
│   │   ├── moex_der_account.png
│   │   ├── moex_der_blocked.png
│   │   ├── moex_der_common.png
│   │   ├── moex_der_group_common.png
│   │   ├── moex_der_groups.png
│   │   ├── moex_der_history.png
│   │   ├── moex_der_margin.png
│   │   ├── moex_der_param.png
│   │   ├── moex_der_profit.png
│   │   ├── moex_der_symbols.png
│   │   ├── moex_der_sync.png
│   │   ├── moex_der_variation.png
│   │   ├── moex_fx_account.png
│   │   ├── moex_fx_common.png
│   │   ├── moex_fx_group_common.png
│   │   ├── moex_fx_group_margin.png
│   │   ├── moex_fx_groups.png
│   │   ├── moex_fx_param.png
│   │   ├── moex_fx_symbols.png
│   │   ├── moex_sec_account.png
│   │   ├── moex_sec_common.png
│   │   ├── moex_sec_group_common.png
│   │   ├── moex_sec_group_margin.png
│   │   ├── moex_sec_groups.png
│   │   ├── moex_sec_param.png
│   │   ├── moex_sec_symbols.png
│   │   ├── mt4gateway_common.png
│   │   ├── mt4gateway_external.png
│   │   ├── mt4gateway_groups.png
│   │   ├── mt4gateway_param.png
│   │   ├── mt4gateway_routing.png
│   │   ├── mt4gateway_symbols.png
│   │   ├── mt4gateway_translations.png
│   │   ├── mt5gateway_common.png
│   │   ├── mt5gateway_groups.png
│   │   ├── mt5gateway_margin.png
│   │   ├── mt5gateway_param.png
│   │   ├── mt5gateway_routing_common.png
│   │   ├── mt5gateway_routing_dealers.png
│   │   ├── mt5gateway_scheme.png
│   │   ├── mt5gateway_symbols.png
│   │   ├── mt5gateway_translations.png
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_10.png
│   │   ├── next_11.png
│   │   ├── next_12.png
│   │   ├── next_13.png
│   │   ├── next_2.png
│   │   ├── next_3.png
│   │   ├── next_4.png
│   │   ├── next_5.png
│   │   ├── next_6.png
│   │   ├── next_7.png
│   │   ├── next_8.png
│   │   ├── next_9.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   ├── previous_10.png
│   │   ├── previous_11.png
│   │   ├── previous_12.png
│   │   ├── previous_13.png
│   │   ├── previous_2.png
│   │   ├── previous_3.png
│   │   ├── previous_4.png
│   │   ├── previous_5.png
│   │   ├── previous_6.png
│   │   ├── previous_7.png
│   │   ├── previous_8.png
│   │   └── previous_9.png
│   ├── Integral.md
│   ├── Interactive-Brokers.md
│   ├── LMAX-Global.md
│   ├── MetaTrader-4.md
│   ├── MetaTrader-5.md
│   ├── MOEX-Derivatives.md
│   ├── MOEX-Securities.md
│   └── MOEXFX.md
├── Gateways.md
├── History-Server/
│   ├── Console-Commands.md
│   ├── images/
│   │   ├── filtration_scheme.png
│   │   ├── filtration_scheme_acceptable.png
│   │   ├── filtration_scheme_discard.png
│   │   ├── filtration_scheme_hard.png
│   │   ├── filtration_scheme_next.png
│   │   ├── filtration_scheme_previous.png
│   │   ├── filtration_scheme_soft.png
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_2.png
│   │   ├── next_3.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   ├── previous_2.png
│   │   └── previous_3.png
│   ├── Interaction-with-Quote-Providers.md
│   ├── Quotes-Filtration.md
│   └── Structure-of-Directories-and-Files.md
├── History-Server.md
├── images/
│   ├── next.png
│   ├── next_1.png
│   ├── next_2.png
│   ├── next_3.png
│   ├── next_4.png
│   ├── next_5.png
│   ├── next_6.png
│   ├── next_7.png
│   ├── previous.png
│   ├── previous_1.png
│   ├── previous_2.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   ├── previous_6.png
│   ├── previous_7.png
│   ├── refresh_configuration_button.png
│   ├── restart_server_button.png
│   ├── web-terminal.png
│   ├── webterminal_customize.png
│   ├── webterminal_mobile.png
│   ├── webterminal_new.png
│   ├── webterminal_new_mobile.png
│   ├── webterminal_utm.png
│   ├── webterminal_utm_1.png
│   ├── webterminal_version.png
│   └── webterminal_webservices.png
├── Old-WebTerminal.md
├── Trade-Server/
│   ├── Daily-Reports.md
│   ├── images/
│   │   ├── groups_reports.png
│   │   ├── network_add_eod.png
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_2.png
│   │   ├── next_3.png
│   │   ├── next_4.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   ├── previous_2.png
│   │   ├── previous_3.png
│   │   └── previous_4.png
│   ├── Mail-Templates.md
│   ├── Return-Errors.md
│   ├── SendMail-Utility.md
│   └── Structure-of-Directories-and-Files.md
├── Trade-Server.md
└── WebTerminal.md
```

---

## 📄 Files

<a id='access-server-md'></a>
### 119. `Access-Server.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / Access Server

[Previous](Trade-Server/Return-Errors.md) | [Next](Access-Server/Structure-of-Directories-and-Files.md)

# Access Server

Access servers are proxy servers and the platform firewalls at the same time. They perform the following functions:

  * Processing of incoming client connections.
  * Packing authorization requests and sending them to the trade server.
  * Checking activity of client connections protecting the trade server from attacks and overload ([antiflood control](Access-Server/Antiflood-Control.md)).
  * Saving history data, depth of market and news, and translate them to clients, thus reducing the load to the history server.
  * Cashing and providing [Live Update](../Platform-Setup/Live-Update.md) to terminals.
  * [Monitoring (#witness)](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#witness) the operation of the history and trade servers.



The unlimited number of access servers can exist for each trade server. Terminals are switched between them automatically, depending on the [priority](Access-Server/Priority.md) settings.

  * For server configuration details, see the ["Network cluster"](../Platform-Setup/Network-cluster/Configuring-Servers.md) section.


  * Use the [Access Server hosting from MetaQuotes](../Platform-Setup/Network-cluster/Hosted-Access-Servers.md) to quickly and safely deploy an access server in the desired region. 

  
---

```

---

<a id='backup-server-md'></a>
### 119. `Backup-Server.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / Backup Server

[Previous](History-Server/Console-Commands.md) | [Next](Backup-Server/Backup-Features.md)

# Backup Server

Servers of this type are used for creating backup copies of data that will be used in case of the trade or history server failure. They perform the following functions:

  * They provide the real-time backuping of the trade server and the history server. Each server is associated with one or more separate backup server instances which can replace it at any time.
  * They create backups of all databases every day, besides they perform regular backups of client and trade bases.
  * When backuping a history server they create real time backups of data required for correct restoring of [gateways](../Platform-Setup/Gateways.md): custom settings that can be stored (at developer's discretion) in the settings.dat file in a gateway work folder, and trade executions database.
  * They provide [automatic failover (#auto)](Backup-Server/Switching-to.md#auto) in case the primary server becomes unavailable.
  * Using backup servers, you can easily [migrate servers (#manual)](Backup-Server/Switching-to.md#manual) to new hardware.
  * Backup servers enable you to quickly [restore](Backup-Server/Restoring-Server.md) server operation in the manual mode even if the main trade server is unavailable, and connection to the platform via MetaTrader 5 Administrator is not possible.
  * [Replicate information](Backup-Server/SQL-Export.md) to database managed by MySQL, MariaDB, PostgreSQL, Firebird, MSSQL or Oracle.



> For server configuration details, please see the ["Network cluster"](../Platform-Setup/Network-cluster/Configuring-Servers.md) section.

```

---

<a id='data-feeds-md'></a>
### 119. `Data-Feeds.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / Data Feeds

[Previous](Backup-Server/SQL-Export/mt5-gateways-symbols.md) | [Next](Data-Feeds/Dow-Jones-Prime-Tass-News-Feeder.md)

# Data Feeds

Data feeds enable receipt of quotes and news in the online trading platform. They transmit information to [the history server](History-Server.md), from which the are translated to [access points](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md) (data centers) and terminals. The trading platform includes several data feeds that enable receiving of quotes and news from the most popular feed providers:

  * [Dow Jones Prime Tass News Feeder](Data-Feeds/Dow-Jones-Prime-Tass-News-Feeder.md)
  * [DJ News Feeder](Data-Feeds/DJ-News-Feeder.md)
  * [IQFeeder](Data-Feeds/IQFeeder.md)
  * [MetaTrader 4 Feeder](Data-Feeds/MetaTrader-4-Feeder.md)
  * [MetaTrader 5 Feeder](Data-Feeds/MetaTrader-5-Feeder.md)
  * [Trading Central News Feeder](Data-Feeds/Trading-Central-News-Feeder.md)
  * [MetaTrader 5 UniFeeder](Data-Feeds/MetaTrader-5-UniFeeder.md)
  * [Thomson Reuters Feeder](Data-Feeds/Thomson-Reuters-Feeder.md)
  * [RSS News Feeder](Data-Feeds/RSS-News-Feeder.md)
  * [IBTimes News Feeder](Data-Feeds/IBTimes-News-Feeder.md)
  * [ForexPros Feeder](Data-Feeds/ForexPros-Feeder.md)
  * [KnowledgeView News Feeder](Data-Feeds/KnowledgeView-News-Feeder.md)
  * [FXstreet Feeder](Data-Feeds/FXstreet-Feeder.md)
  * [Financial Source News Feeder](Data-Feeds/Financial-Source-News-Feeder.md)
  * [Claws & Horns Feeder](Data-Feeds/Claws-&-Horns-Feeder.md)
  * [UniNewsFeeder ](Data-Feeds/UniNewsFeeder.md)
  * [Alliance News Feeder](Data-Feeds/Alliance-News-Feeder.md)
  * [Newsquawk](Data-Feeds/Newsquawk.md)
  * [Remote Datafeed](Data-Feeds/Remote-Datafeed.md)
  * [Universal DDE Connector](Data-Feeds/Universal-DDE-Connector.md)



Data feeds are executable filed (with extension *.exe) that are run as separate processes. These executable files must be located in the datafeed folder of [the history server (#datafeed)](History-Server/Structure-of-Directories-and-Files.md#datafeed).

> If the data feed file is copied to the above mentioned folder while the platform is operating, the history server needs to be restarted (select it in the ["Network"](../Platform-Setup/Network-cluster.md) section and execute the "![Restart](images/restart_server_button.png) Restart" command in the ["Services"](../MetaTrader-5-Administrator/User-Interface/Main-Menu/Services.md) menu or in the [context menu (#context)](../Platform-Setup/Network-cluster.md#context)). After that refresh configurations in the administrator terminal by pressing "![Refresh configuration](images/refresh_configuration_button.png) Refresh configuration".

In order to use a data feed, connection to the feed provider server needs to be established. Data delivery from a third party vendor is implemented based on a special agreement.

```

---

<a id='gateways-md'></a>
### 119. `Gateways.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / Gateways

[Previous](Data-Feeds/Universal-DDE-Connector/UniFeeder-Protocol.md) | [Next](Gateways/MOEXFX.md)

# Gateways

Gateways are intended for integration of the MetaTrader 5 platform with external trade systems. Gateways allow bringing out trade operation to external systems as well as translating quotes and news from them. Gateways are executable files (*.exe) that run as separate processes.

The trading platform includes many gateways.

## Liquidity Gateways

  * [MetaTrader 5 Gateway to Currenex](Gateways/Currenex.md)
  * [MetaTrader 5 Gateway to Integral](Gateways/Integral.md)
  * [MetaTrader 5 Gateway to Euronext FX](Gateways/Euronext-FX.md)
  * [MetaTrader 5 Gateway to Cboe FX](Gateways/Cboe-FX.md)
  * [MetaTrader 5 Gateway to LMAX Global](Gateways/LMAX-Global.md)
  * [MetaTrader 5 Gateway to FXCM PRO](Gateways/FXCM-PRO.md)
  * [MetaTrader 5 Gateway to MetaTrader 5](Gateways/MetaTrader-5.md "MetaTrader 5 Gateway to MetaTrader 5")
  * [MetaTrader 5 Gateway to MetaTrader 4](Gateways/MetaTrader-4.md)



## Exchange Gateways

  * [MetaTrader 5 Gateway to MOEXFX](Gateways/MOEXFX.md) (Moscow Exchange, FX market)
  * [MetaTrader 5 Gateway to MOEX Securities](Gateways/MOEX-Securities.md) (Moscow Exchange, Securities market)
  * [MetaTrader 5 Gateway to MOEX Derivatives](Gateways/MOEX-Derivatives.md) (Moscow Exchange, Derivatives market)
  * [MetaTrader 5 Gateway to DGCX](Gateways/DGCX.md "MetaTrader 5 Gateway to DGCX") (Dubai Gold & Commodities Exchange, Derivatives market)
  * MetaTrader 5 Gateway to Ukrainian Exchange (Stocks)
  * MetaTrader 5 Gateway to ASX (Australian Securities Exchange, Futures and Stocks)
  * [MetaTrader 5 Gateway to Borsa Istanbul Futures](Gateways/Borsa-Istanbul.md) (Derivatives market VIOP)
  * [MetaTrader 5 Gateway to Interactive Brokers](Gateways/Interactive-Brokers.md)



```

---

<a id='history-server-md'></a>
### 119. `History-Server.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / History Server

[Previous](Access-Server/Priority.md) | [Next](History-Server/Structure-of-Directories-and-Files.md)

# History Server

The history server processes price and news data. This server performs the following functions:

  * Receiving and filtering price and news data from gateways and datafeeds.
  * Packing price and news data.
  * Storing and providing price history in the form of 1-minute bars and ticks to other components of the platform.
  * Storing and providing the news thread.
  * Receiving, checking and distributing [Live Updates](../Platform-Setup/Live-Update.md) among the MetaTrader 5 platform components.



> For server configuration details, see the ["Network cluster"](../Platform-Setup/Network-cluster/Configuring-Servers.md) section.

```

---

<a id='old-webterminal-md'></a>
### 119. `Old-WebTerminal.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / Old WebTerminal

[Previous](WebTerminal.md) | [Next](../Platform-Setup.md)

<a id="metatrader-5-webterminal"></a>
# MetaTrader 5 WebTerminal (#metatrader-5-webterminal)

> This section describes the old version of the web terminal. It will be supported for a limited time. We recommend upgrading to the [new, improved Web Terminal version](WebTerminal.md) the soonest possible. 

The MetaTrader 5 WebTerminal enables financial market trading using any web browser. It works in all operating systems and browsers, while requiring no extra software installations. All transmitted data is securely encrypted.

The web terminal supports all types of market and pending orders, as well as one-click trading. Traders can view real-time quotes and analyze charts using basic graphical objects. Charts can be analyzed using 30 technical indicators.

The terminal is a modern HTML5 application that can be easily integrated into any website via a simple iframe widget.

Similar to the desktop platform, traders should select a server from the list, enter login and password when connecting to the web terminal via your website. For the seamless web terminal integration with clients area on your website, server and login can be pre-selected to let your client enter a password only. If a users saves a password in a browser storage, the platform will login to the trading account automatically on the next run.

![MetaTrader 5 WebTerminal](images/web-terminal.png)

To get the terminal, [order it in the App Store section](https://support.metaquotes.net/en/market/product/251 "Order MetaTrader 5 WebTerminal") of the Support website.

[Order WebTerminal](https://support.metaquotes.net/en/market/product/251 "Order WebTerminal") [Configure WebTerminal (# "configure webterminal")](https://support.metaquotes.net/en/market/whitelabel/mt5# "configure webterminal")

  * The trading platform should be updated to at least build 1325 for the web terminal operation.
  * [MQL5.community](https://mql5.com "MQL5.community") account is not required.

  
---  
  
<a id="how-to-add-the-webterminal-widget-to-your-website"></a>
## How to Add the WebTerminal Widget to Your Website (#how-to-add-the-webterminal-widget-to-your-website)

To install the WebTerminal widget on your site, visit the "[App Store \ White Labels \ MetaTrader 5 ](https://support.metaquotes.net/en/market/whitelabel/mt5#)" section of the technical support site. Then click "Show widget code \ Customize":

![Customize the WebTerminal widget](images/webterminal_customize.png)

Set the WebTerminal operation parameters. After that, a special code will be generated for you, which should be inserted into your website.

The following parameters are supported (the corresponding parameters in the widget code are displayed in brackets, you can change them manually if necessary).

  * Version (version) — default web terminal version: MetaTrader 4 or MetaTrader 5. The parameter is important only if you use both versions of the platform at the same time — if the widget settings have no restrictions on used servers or the servers of both versions are present in the server list (servers). The parameter is used only for the first launch of the web terminal. Further on, the platform version will be defined based on the last used account. The detailed description is given in the section [If you have two platforms: MetaTrader 5 and MetaTrader 4 (#version)](Old-WebTerminal.md#version).
  * Restrict trade servers \ Trade server list (servers) — limit servers available for use in your web terminal. All servers of all brokers are available by default. Simply enter a name in the new account opening or in the existing account login dialog.  
If you enable the "Restrict trade servers" option and set the list of available servers, the list of certain servers instead of the server name input box will be available in the appropriate dialogs.



> Server names are case sensitive. Be sure to specify the exact name.

  * Default login (login) — default trading account selected in the login dialog. Use this option to create convenient client areas by immediately substituting the necessary account into the web terminal.
  * Default trade server (server) — default server selected in the connection dialog. Use this option to create convenient client areas by immediately substituting the necessary server into the web terminal.
  * Allow opening demo accounts on any servers (demoAllServers) — disable the option if you want to allow opening demo accounts via the web terminal only on demo servers from the "Trade server list" parameter. If enabled, demo accounts can be opened on any servers (regardless of the "Restrict trade servers" parameter). The server name input box is displayed instead of the list of available servers in the appropriate dialog.
  * Demo account types (demoType) — demo account type, multiple comma-separated values can be added. To open demo accounts in the "demoforex" group, specify "forex" (the "demo" prefix is added automatically). If not specified, all account types configured in the "[Allocations](../Platform-Setup/Accounts/Account-Allocation-Settings.md)" are used. At the moment, you can add this parameter to the terminal widget only by specifying it in the code manually.
  * Leverage (demoLeverage) — the leverage for the demo account, multiple comma separated options can be added. If not specified, all options configured in the "[Allocations](../Platform-Setup/Accounts/Account-Allocation-Settings.md)" are used. At the moment, you can add this parameter to the terminal widget only by specifying it in the code manually.
  * First Name and Second Name (demoFirstName, demoSecondName) — the first name and the second name to be automatically inserted into the demo account registration form in the web terminal. These parameters can be added to the embed code only manually. Use the parameters to display the web terminal with appropriate data to the users who are authorized on the site and whose first and second name are known.
  * Email (demoEmail) — the email address to be automatically inserted into the demo account registration form in the web terminal. Thia parameter can only be added to the embed code manually. Use the parameter to display the web terminal with appropriate data to the users who are authorized on the site and whose emails are known in advance.
  * Allow the Phone field in the demo account opening dialog (demoAllowPhone) — show the Phone input box in the demo account registration form ("true" value).
  * UTM campaign \ UTM Source (utmCampaign \ utmSource) — UTM tags to be added to accounts opened via the web terminal. The tags allow you to analyze the efficiency of this tool. For more details, see ["How to track accounts opened via the web terminal" (#track)](Old-WebTerminal.md#track).
  * Width (width) — terminal widget width in % or pixels. The recommended value is 100% to allow the web terminal to automatically adjust to the maximum available width on the web page.
  * Height (height) — terminal widget height in % or pixels. The recommended value is "600px" to make the entire widget visible even on small screens without the need to scroll.
  * What to do at the start for new visitors (startMode) — web terminal launch mode:


  * Open the demo account creation dialog (open_demo) — display a demo account opening window (instead of the login window) for users who do not have accounts stored in the web terminal. If accounts exist in the local storage, connection to the last used account is established.
  * Create a demo account automatically (create_demo) — open a demo account automatically for a user when launching the web terminal. The account is opened only if the user's web terminal has no previously saved accounts.
  * Show login dialog (login) — show account login window for users when launching the web terminal. Login to the last used account is not conducted automatically even if a user saved the account password in the browser storage previously.
  * Symbols (symbols) — list of symbols to be displayed by default in the "Market Watch" window of the web terminal (optional). The parameter also defines the display order of the symbols. For example, if you add ["EURUSD", "EURGBP", "AUDUSD", "EURRUB"] to the widget, a user will see only the four specified symbols in the "Market Watch" window after the first launch of the web terminal. EURUSD will be displayed first, while EURRUB will be last. Subsequently, the user can re-configure the list of symbols and the settings will be saved in the browser. The maximum number of symbols in the parameter is 300.
  * Chart color scheme (colorScheme) — default color scheme applied to charts. Possible values: black_on_white, yellow_on_black and green_on_black.
  * Language (lang) — default web terminal interface language. Users can select a necessary language in the web terminal menu: View -> Languages. In this case, the value of this parameter is ignored. Currently, the following languages are supported:


  * Arabic (ar)
  * Bulgarian (bg)
  * Chinese (zh)
  * Croatian (hr)
  * Czech (cs)
  * Danish (da)
  * Dutch (nl)
  * English (en)
  * Estonian (et)
  * Finnish (fi)
  * French (fr)
  * German (de)
  * Greek (el)
  * Hebrew (he)
  * Hindi (hi)
  * Hungarian (hu)
  * Indonesian (id)
  * Italian (it)
  * Japanese (ja)
  * Korean (ko)
  * Latvian (lv)
  * Lithuanian (lt)
  * Malay (ms)
  * Mongolian (mn)
  * Persian (fa)
  * Polish (pl)
  * Portuguese (pt)
  * Romanian (ro)
  * Russian (ru)
  * Serbian (sr)
  * Slovak (sk)
  * Slovenian (sl)
  * Spanish (es)
  * Swedish (sv)
  * Tajik (tg)
  * Thai (th)
  * Traditional Chinese (zt)
  * Turkish (tr)
  * Ukrainian (uk)
  * Uzbek (uz)
  * Vietnamese (vi)



Sample web terminal code to be inserted into a website:

<div id="webterminal" style="width:100%;height:600px;"></div>   
<script type="text/javascript" src="https://metatraderweb.app/trade/widget.js"></script>   
<script type="text/javascript">   
new MetaTraderWebTerminal( "webterminal", {   
version: 5,   
server: "MetaQuotes-Demo",   
demoAllServers: true,   
startMode: "create_demo",   
lang: "en",   
colorScheme: "black_on_white"   
} );   
</script>  
---  
  
> Configuring the account opening form (type, leverage, balance)

<a id="track"></a>
## How to track accounts opened via the web terminal (#track)

Special UTM parameters are added to all demo accounts opened from the web terminal. Such UTM tags inform the broker that the potential client has come from a web terminal operating on the broker's website. The tags are added to the [trading account parameters (#leadsource)](../Platform-Setup/Accounts/Editing-Account.md#leadsource):

  * The Comment field contains the following details: "WebTerminal [the short name of the domain from which the account was opened]". Example: "WebTerminal mysite.com". The "www" part is removed from the address.
  * The domain name with 'www' is also added in the 'Lead source'‌ field. Example: "www.mysite.com". The value can be overridden by adding utm_source to the widget parameters.
  * The 'Lead campaign' field is not filled by default. You may add utm_campaign to widget parameters in order to write the name of your marketing campaign to this field.



To use your own UTM parameters for tracking clients, add the [utmSource and utmCampaign parameters (#utm)](Old-WebTerminal.md#utm) to the web terminal widget.

<div id="webterminal" style="width:100%;height:600px;"></div>   
<script type="text/javascript" src="https://metatraderweb.app/trade/widget.js"></script>   
<script type="text/javascript">   
new MetaTraderWebTerminal( "webterminal", {   
version: 5,   
server: "MetaQuotes-Demo",   
utmCampaign: "www.abcbroker.com",   
utmSource: "web.demo",   
demoAllServers: true,   
startMode: "create_demo",   
lang: "en",   
colorScheme: "black_on_white"   
} );   
</script>   
</script>  
---  
  
For the widget added to the www.abcbroker.com site, account parameters will be filled as follows:

  * Comment = abcbroker.com
  * Lead source = www.abcbroker.com
  * Lead campaign = web.demo



![Tracking account registrations via the web terminal](images/webterminal_utm_1.png)

<a id="detecting-the-webterminal-language"></a>
## Detecting the WebTerminal Language (#detecting-the-webterminal-language)

The web terminal determines the interface language based on the following priorities:

  * The language selected by the user in the web terminal
  * The language specified in lang (if the language is supported in the web terminal)
  * The preferred language in the user's web browser (if the language is supported in the web terminal)



If the web terminal cannot determine the language, English will be used.

<a id="operation-features"></a>
## Operation Features (#operation-features)

The maximum number of symbols a client can enable in the Market Watch window is 300 for all browsers, except for Internet Explorer/Edge — 50. A greater number of symbols in Internet Explorer/Edge slows down the web terminal operation.

<a id="mobile"></a>
## Mobile version of the web platform (#mobile)

The MetaTrader 5 web platform includes a special version adapted for smartphones. This allows for convenient trading from mobile browsers in addition to desktop ones. If your website has a mobile version, make sure the appropriate version of the web platform is used there, so that your traders are able to comfortably work from their smartphones. This web platform version can also be embedded directly into mobile Android and iOS applications using the WebView component.

![Mobile version of the MetaTrader 5 web platform](images/webterminal_mobile.png)

To launch the mobile version of the web platform, add the "mobile: 1" parameter to the widget. Since the mobile version of the web platform is available only for the MetaTrader 5 platform, we also recommend setting the "version=5" parameter to ensure its launch.

<!DOCTYPE html>   
<html>   
<head>   
<meta charset="UTF-8">   
<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">   
<title>Web Terminal</title>   
</head>   
<body>   
<div id="webterminal" style="width:100%;height:600px;"></div>   
<script type="text/javascript" src="https://metatraderweb.app/trade/widget.js"></script>   
<script type="text/javascript">   
new MetaTraderWebTerminal("webterminal", {   
version: 5,   
server: "MetaQuotes-Demo",   
demoAllServers: true,   
startMode: "create_demo",   
lang: "en",   
mobile: 1,   
colorScheme: "black_on_white"   
});   
</script>   
</body>   
</html>  
---  
  
To call the web platform in your mobile application, create a web form and load the web platform address with the "m=1" and "version="5" parameters to it (similar to the iframe widget). In order to simplify the task, we have prepared examples in the form of simple iOS and Android projects:

  * [Sample Android (Java) project](https://support.metaquotes.net/spfiles/metatrader5/webterminal-mobile-android-example.zip)
  * [Sample iOS (Swift) project](https://support.metaquotes.net/spfiles/metatrader5/webterminal-mobile-ios-example.zip)



> The mobile version is supported only in the MetaTrader 5 web platform.

<a id="version"></a>
## If you have two platforms: MetaTrader 5 and MetaTrader 4 (#version)

A single web terminal is used for both platform versions. If you only use one platform (MetaTrader 4 or MetaTrader 5), no additional actions are required. Simply select the necessary one [when receiving the code for insertion (#version-param)](Old-WebTerminal.md#version-param). 

If you simultaneously use two versions of the trading platform, you do not need to configure WebTerminals separately. If the web terminal finds servers of both versions in the "[Trade server list (#servers)](Old-WebTerminal.md#servers)" parameter, a switch between the two versions appears in the web terminal interface. It is available in the account connection dialog, in the account opening dialog and in the File menu.

![Switching between WebTerminal Versions](images/webterminal_version.png)

<a id="setting-the-default-version"></a>
### Setting the default version (#setting-the-default-version)

In order to set a default version that will be selected during the web terminal launch, use the [Version parameter (#version-param)](Old-WebTerminal.md#version-param):

<div id="webterminal" style="width:100%;height:600px;"></div>   
<script type="text/javascript" src="https://metatraderweb.app/trade/widget.js"></script>   
<script type="text/javascript">   
new MetaTraderWebTerminal( "webterminal", {   
version: 5,   
servers: ["ForexBroker4-Live","ForexBroker5-Live"],   
demoAllServers: true,   
startMode: "create_demo",   
lang: "en",   
colorScheme: "black_on_white"   
} );   
</script>  
---  
  
In this example, the versions switch is set to MetaTrader 5 by default.

If a user switches to another platform, the selection will be remembered. During the next launch of the WebTerminal, it will be switched to the latest used version of the platform.

<a id="supported-browser-versions"></a>
## Supported Browser Versions (#supported-browser-versions)

The web terminal supports the following web browser versions and above:

  * Internet Explorer 11
  * Microsoft Edge 12
  * Mozilla Firefox 34
  * Google Chrome 43
  * Safari 8
  * Opera 32



<a id="example-of-adding-a-webterminal-widget"></a>
## Example of Adding a WebTerminal Widget (#example-of-adding-a-webterminal-widget)

<!DOCTYPE html>   
<html lang="en">   
<head>   
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">   
<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">   
<title>WebTerminal for the MetaTrader 4 and MetaTrader 5 platforms</title>   
<style type="text/css">   
body {margin: 0; padding: 0; font-family: Arial, Tahoma; font-size: 16px; color: #000; background-color: #FFF; min-width: 1010px}   
.top {background-color: #0055A7;}   
.top h1 {margin: 10px 20px 10px 10px; font-size: 25px; font-weight: normal; color: #FFF; display: inline-block; vertical-align: middle; }   
.top .menu, .top .menu li {margin: 0; padding: 0; list-style: none; display: inline-block; vertical-align: middle; }   
.top .menu li {margin: 0; padding: 0; list-style: none; display: inline-block;}   
.top .menu li a {padding: 20px; font-size: 16px; color: #FFF; text-decoration: none; text-align: center; display: block;}   
.top .menu li a:hover {background-color: #0B6ABF;}   
.top .menu li a.selected {background-color: #2989DF; color: #FFF;}   
.content { box-shadow: 0 0 20px rgba(0,0,0,0.5); position: relative; }   
.footer {text-align: center; padding: 20px; color: #0A0A0A; font-size: 14px}   
</style>   
</head>   
<body>   
<div class="top">   
<h1>BROKER</h1>   
<ul class="menu">   
<li><a href="#">Analytics</a></li>   
<li><a href="#" class="selected">WebTerminal</a></li>   
<li><a href="#">News</a></li>   
<li><a href="#">Contacts</a></li>   
</ul>   
</div>   
<div class="content">   
<!-- Web Terminal Code Start -->   
<div id="webterminal" style="width:100%;height:600px;"></div>   
<script type="text/javascript" src="https://metatraderweb.app/trade/widget.js"></script>   
<script type="text/javascript">   
new MetaTraderWebTerminal( "webterminal", {   
version: 5,   
server: "MetaQuotes-Demo",   
demoAllServers: true,   
startMode: "create_demo",   
lang: "en",   
colorScheme: "black_on_white"   
} );   
</script>   
<!-- Web Terminal Code End -->   
</div>   
<div class="footer">   
Copyright 2000-2015, Broker   
</div>   
</body>   
</html>  
---

```

---

<a id='trade-server-md'></a>
### 119. `Trade-Server.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / Trade Server

[Previous](../Platform-Components.md) | [Next](Trade-Server/Structure-of-Directories-and-Files.md)

# Trading Server

The system has two types of trading servers: one main server server and additional ones. The main trading server serves trading operations and manages the entire system configuration.

The trading server performs the following functions:

  * Storing and management of clients' records.
  * Authentication and authorization of client connections.
  * Storing and management of trade records.
  * Check, management and execution of trade requests.
  * Management of the internal mailing system.



  * One main trading server and the unlimited number of additional ones can be configured in the system.
  * For server configuration details, please see the ["Network cluster"](../Platform-Setup/Network-cluster/Configuring-Servers.md) section.

  
---

```

---

<a id='webterminal-md'></a>
### 119. `WebTerminal.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../Platform-Components.md) / WebTerminal

[Previous](Gateways/Interactive-Brokers.md) | [Next](Old-WebTerminal.md)

<a id="metatrader-5-webterminal"></a>
# MetaTrader 5 WebTerminal (#metatrader-5-webterminal)

The MetaTrader 5 WebTerminal enables financial market trading using any web browser. It works in all operating systems and browsers, while requiring no extra software installations. All transmitted data is securely encrypted.

The web terminal supports all types of market and pending orders, as well as one-click trading. Traders can view real-time quotes and analyze charts using basic graphical objects. Charts can be analyzed using 30 technical indicators.

The terminal is a modern HTML5 application that can be easily integrated into any website via a simple iframe widget.

The web terminal is located entirely on the broker's access servers. It operates as an individual web terminal, which only works with your platform. This provides maximum security and full control for the broker.

When connecting to the web terminal via your website, the trader should only enter the login and password, without having to select a server. The platform will determine which server (demo, real, main or additional trading server) the account belongs to. For the seamless web terminal integration with the clients area on the broker website, the user login can be pre-selected to let your client enter a password only. If a user saves a password in a browser storage, the account will be connected automatically on the next run.

![MetaTrader 5 Web Terminal](images/webterminal_new.png)

  * The web terminal only operates with the trading platform version 3440 or higher.
  * If your platform license does not include the web terminal, [order it via the App Store section](https://support.metaquotes.net/en/market/product/248 "Order MetaTrader 5 Web Terminal") of the Support Center website.

  
---  
  
<a id="how-to-set-up-the-platform"></a>
## How to set up the platform (#how-to-set-up-the-platform)

The web terminal operates on an [access server](Access-Server.md) which acts as a web server.

Register a domain (or a subdomain for your existing domain) where the web terminal will run. Below we use the domain webtrading.broker.com as an example — you should replace it with your own domain.

Associate your domain with the [public IP address (#public)](../Platform-Setup/Network-cluster/Configuring-Servers.md#public) of your access server. For this purpose, the appropriate record must be specified on the DNS hosting. For example, for webtrading.broker.com host, the following entry should be registered in DNS: "XXX.XXX.XXX.XXX webtrading.broker.com", where XXX.XXX.XXX.XXX is the public address of the access server.

Next, open [Integration \ Web services](../Platform-Setup/Integrations/Web-Services.md) in MetaTrader 5 Administrator and add an SSL certificate for the domain. The certificate will enable connections to the access server using the HTTPS protocol.

You can add extra certificates for your White Label partners to provide a separate web terminal for each required company's domain. After that, in the relevant field, specify which company the domain belongs to.

![Add a certificate for the domain where the web terminal will run](images/webterminal_webservices.png)

It is recommended to have port 443 available on the server for HTTPS connections. In this case, your clients will not need to explicitly specify the port in the address bar to open the web terminal page.

No other settings are needed. Your web terminal will be available at https://webtrading.broker.com/terminal/.

<a id="if-you-have-multiple-access-servers"></a>
## If you have multiple access servers (#if-you-have-multiple-access-servers)

For each platform we [recommend (#recommended)](../Platform-Installation/System-Requirements.md#recommended) using at least two access servers: for the main and backup configuration. As your customer database grows and your business geography expands, the number of servers will increase to ensure high-quality service.

To enable connections to your web terminal via any of your access servers, add A-records with their public addresses to the DNS server. Thus, you will have several records with different addresses but with the same domain:

XXX.XXX.XXX.XXX webtrading.broker.com YYY.YYY.YYY.YYY webtrading.broker.com ZZZ.ZZZ.ZZZ.ZZZ webtrading.broker.com  
---  
  
XXX, YYY and ZZZ are the addresses of your access servers. There can be any number of them.

No additional actions are required on the platform side. The domain certificate uploaded via the Integration \ Web Services section is used for all access servers.

To balance the load by distributing connections to the web terminal between access servers, use GeoDNS or GLSB services. Please check with your hosting provider whether this service is available.

<a id="if-you-hold-multiple-licenses"></a>
## If you hold multiple licenses (#if-you-hold-multiple-licenses)

If you have multiple MetaTrader 5 platform licenses, for example, the main cluster for live accounts and an [additional cluster for demo accounts](https://support.metaquotes.net/en/market/product/569), you should configure web terminals separately for each of them. The web terminal runs on access servers which belong to a particular platform, and thus they do not know about the existence of other platforms.

With such a configuration, you will have different web terminal links for each platform. You need to provide the option to select the desired platform for your customers. For example, you can implement a drop-down list on your website.

<a id="how-to-add-the-web-terminal-to-your-site"></a>
## How to add the web terminal to your site (#how-to-add-the-web-terminal-to-your-site)

To install the web terminal on your site, simply place the <iframe> tag on the desired page. The address of your web terminal should be specified as the source in this tag:

<!DOCTYPE html>   
<html>   
<head>   
<meta charset="UTF-8">   
<title>Web Terminal</title>   
</head>   
<body>   
<iframe src="https://webtrading.broker.com/terminal?mode=connect&marketwatch=EURUSD,GBPUSD,USDJPY&utm_campaign=webterminal&utm_source=site" width="100%" height="1000"></iframe>   
</body>   
</html>  
---  
  
Additional web terminal settings can be specified as URL parameters:

<iframe src="https://webtrading.broker.com/terminal?parameter1=value1&parameter2=value2"></iframe>  
---  
  
The following parameters are supported:

first_name, second_name, email — first name, last name and email to be inserted into the demo and real account registration form. By using these parameters, you can make account opening easier for traders who have already registered on your site and provided the required data. Example:

https://webtrading.broker.com/terminal?mode=demo&first_name=John&second_name=Smith&email=johnsmith%40mail.com  
---  
  
Please note that the example includes the "mode=demo" parameter to automatically open the demo account registration form upon the web terminal launch.

utm_campaign, utm_source — utm parameters that will be added to the [relevant fields of accounts (#leadsource)](../Platform-Setup/Accounts/Editing-Account.md#leadsource) opened via the web terminal. Using them, you can analyze how efficiently you attract traders via web terminals. For further details please see ["How to track accounts opened via the web terminal" (#track)](WebTerminal.md#track). Example:

https://webtrading.broker.com/terminal?utm_campaign=webterminal&utm_source=site  
---  
  
The parameters are used only at the first start. After that the web terminal will use the user-specified data. 

mode — the web terminal page that opens on first launch. Supported values:

  * demo — demo account registration form
  * real — real account registration form
  * connect — existing account connection form



https://webtrading.broker.com/terminal?mode=connect  
---  
  
The parameter is used only if the user has not previously connected to the account. If the web terminal has a saved account, it will be connected immediately upon startup.

login — trading account for connection. If this parameter is specified, the web terminal will be launched with a pre-filled account connection dialog. The user will only have to enter a password. Use this parameter to create convenient client areas.

https://webtrading.broker.com/terminal?login=123456  
---  
  
If an account is specified in the URL, no demo account will be crated at the first launch (the option is managed via [platform settings](../Platform-Setup/Accounts/Account-Allocation-Settings.md)). This also prevents from connecting using a previously saved account.

marketwatch — the list of symbols to be displayed by default in Market Watch is specified by the marketwatch parameter. Example:

https://webtrading.broker.com/terminal?marketwatch=EURUSD,GBPUSD,AUDCAD,USDJPY  
---  
  
The parameter also determines the order in which the symbols are displayed. In the example above, on the first web terminal launch the user will see only four specified symbols in the Market Watch window, EURUSD will be the first and USDJPY will be the last. Later the user can re-configure the list of symbols, and the new settings will be saved in the browser. The maximum number of symbols in the parameter is 300.

theme-mode — theme for the application interface. Possible values:

  * 0 — light (default)
  * 1 — dark



https://webtrading.broker.com/terminal?theme-mode=1  
---  
  
The parameter is only used for the first start. After that the web terminal will use user-specified settings. If necessary, you can force a user-defined theme to be overridden. This may be useful, for example, if your site supports light and dark themes. This will allow the synchronization of interface switching modes of the site and the web terminal.

To switch the color scheme of the web terminal, call postMessage on the <iframe> element, through which the web terminal is loaded. Specify the parameters type: 'mt5_update' and theme-mode: 0 (for the light theme) or 1 (for the dark theme):

const iframe = document.getElementById('iframe');   
  
iframe.contentWindow.postMessage({   
type: 'mt5_update',   
'theme-mode': 1,   
}, '*');  
---  
  
theme — color scheme for the application interface. Possible values:

  * greenRed — red and green (default)
  * blueRed — blue and red
  * blackWhite — black and white
  * neutral — neutral



https://webtrading.broker.com/terminal?theme=blueRed  
---  
  
The parameter is used only at the first start. After that, the web terminal will apply user-specified settings.

The parameter is only used for the first start. Then the web terminal will apply user-specified settings.

lang — web terminal interface language. The following languages are currently supported:

  * English (en), Arabic (ar), Bulgarian (bg), Czech (cs), Chinese Simplified (zh), Chinese Traditional (zt), Hebrew (he), Hungarian (hu), Dutch (nl), French (fr) ), German (de), Greek (el), Hindi (hi),
  * Indonesian (id), Italian (it), Japanese (ja), Korean (ko), Malay (ms), Persian (fa), Polish (pl), Portuguese (pt), Romanian (ro), Russian (ru), Spanish (es), Thai (th), Turkish (tr), Ukrainian (uk), Uzbek (uz), Vietnamese (vi)



https://webtrading.broker.com/terminal?lang=de  
---  
  
The parameter is used only at the first start. After that, the web terminal will apply user-specified settings.

The size of the web terminal window on the page can be set using standard "width" and "height" parameters in the <iframe> tag, for example:

<iframe src="https://webtrading.broker.com/terminal" width="100%" height="1000"></iframe>  
---  
  
Generally we recommended to set the width and height to 100% so that the web terminal block takes up all the available web page space. If you specify an absolute size in pixels, some elements may be out of the visible window on some devices.

<a id="how-to-set-up-the-account-opening-form"></a>
## How to set up the account opening form (#how-to-set-up-the-account-opening-form)

To configure the account opening form, use MetaTrader 5 Administrator. Go to the [Allocations](../Platform-Setup/Accounts/Account-Allocation-Settings.md) section and set available account types, leverages and balance. These settings apply to all terminals, including desktop, mobile and web.

<a id="security-settings"></a>
## Security settings (#security-settings)

Prevent the web terminal page from loading in IFRAME. An attacker can place an invisible IFRAME containing the page of your website with the web terminal and combine the web terminal control element (such as a button) with another link on their website. Thus, when clicking a link, a user may actually perform an action necessary to the attacker.

Add [X-Frame-Options: DENY](https://developer.mozilla.org/en-US/docs/Web/HTTP/X-Frame-Options "Example of X-Frame-Options: DENY configuration") HTTP header to your page containing the web terminal in order to disable page loading in IFRAME and protect users.

Only use the web terminal widget on https pages. The page on which the widget is installed must work over a secure https protocol (not http). Otherwise, the operation of the web terminal will not be possible in some browsers (for example Chrome version 60 and higher).

<a id="track"></a>
## How to track accounts opened via the web terminal (#track)

Special UTM parameters are added to all accounts opened via the web terminal. Such UTM parameters inform the broker that the potential client has come from a web terminal operating on the broker's website. The UTM tags are added to the [trading account parameters (#leadsource)](../Platform-Setup/Accounts/Editing-Account.md#leadsource):

  * The Comment field will contain "WebTerminal [short name of the domain from which the account was opened]". Example: "WebTerminal mysite.com". The "www" part is removed from the address.
  * The domain name with 'www' is also added in the 'Lead source'‌ field. Example: "www.mysite.com". The value can be overridden by adding utm_source to the widget parameters.
  * The 'Lead campaign' field is not filled by default. You may add utm_campaign to widget parameters in order to write the name of your marketing campaign to this field.



To use your own UTM parameters for tracking clients, add the [utm_source and utm_campaign parameters (#utm)](WebTerminal.md#utm) to the web terminal widget.

https://webtrading.broker.com/terminal?utm_campaign=webterminal&utm_source=site  
---  
  
For the widget added to the www.abcbroker.com site, account parameters will be filled as follows:

  * Comment = WebTerminal
  * Lead source = www.abcbroker.com
  * Lead campaign = web.demo



![Tracking account registrations via the web terminal](images/webterminal_utm.png)

<a id="mobile"></a>
## Mobile version of the web platform (#mobile)

The MetaTrader 5 web platform includes a special version adapted for iOS and Android smartphones and tablets. This enables convenient trading from mobile browsers in addition to desktop ones.

No additional settings for the mobile version are needed. The web terminal will automatically detect the user's device by the browser's "user-agent" and will adapt the interface.

![Mobile version of the MetaTrader 5 web platform](images/webterminal_new_mobile.png)

You can also embed a web terminal in your mobile app. To do this, create a web form in it with the web terminal <iframe>.

<a id="minimum-browser-versions"></a>
## Minimum browser versions (#minimum-browser-versions)

The web terminal supports the following web browser versions and above:

  * Microsoft Edge 15
  * Mozilla Firefox 54
  * Google Chrome 51
  * Safari 12
  * Opera 38



<a id="troubleshooting"></a>
## Troubleshooting (#troubleshooting)

If a trader receives a 404 error when trying to open the web terminal page, check the following:

  * The SSL certificate you uploaded in the Integration \ Web Service section is valid and has not expired
  * Your company name is specified correctly in the SSL certificate — it must match the company name specified in the license/White Label
  * Your platform does not run under a test license — in this case the web terminal is not available
  * The web terminal is included in your platform license. Contact the [support team](https://support.metaquotes.net/en/support) to check the license



<a id="web-terminal-widget-example"></a>
## Web terminal widget example (#web-terminal-widget-example)

<!DOCTYPE html>   
<html lang="en">   
<head>   
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">   
<title>WebTerminal for the MetaTrader 5 platforms</title>   
<style type="text/css">   
body {margin: 0; padding: 0; font-family: Arial, Tahoma; font-size: 16px; color: #000; background-color: #FFF; min-width: 1010px}   
.top {background-color: #0055A7;}   
.top h1 {margin: 10px 20px 10px 10px; font-size: 25px; font-weight: normal; color: #FFF; display: inline-block; vertical-align: middle; }   
.top .menu, .top .menu li {margin: 0; padding: 0; list-style: none; display: inline-block; vertical-align: middle; }   
.top .menu li {margin: 0; padding: 0; list-style: none; display: inline-block;}   
.top .menu li a {padding: 20px; font-size: 16px; color: #FFF; text-decoration: none; text-align: center; display: block;}   
.top .menu li a:hover {background-color: #0B6ABF;}   
.top .menu li a.selected {background-color: #2989DF; color: #FFF;}   
.content { box-shadow: 0 0 20px rgba(0,0,0,0.5); position: relative; }   
.footer {text-align: center; padding: 20px; color: #0A0A0A; font-size: 14px}   
</style>   
</head>   
<body>   
<div class="top">   
<h1>BROKER</h1>   
<ul class="menu">   
<li><a href="#">Analytics</a></li>   
<li><a href="#" class="selected">WebTerminal</a></li>   
<li><a href="#">News</a></li>   
<li><a href="#">Contacts</a></li>   
</ul>   
</div>   
<div class="content">   
<!-- Web Terminal Code Start -->   
<iframe src="https://webtrading.broker.com/terminal?mode=connect&marketwatch=EURUSD,GBPUSD,USDJPY&utm_campaign=webterminal&utm_source=site" width="100%" height="1000"></iframe>   
<!-- Web Terminal Code End -->   
</div>   
<div class="footer">   
Copyright 2000-2015, Broker   
</div>   
</body>   
</html>  
---

```

---

<a id='access-server-antiflood-control-md'></a>
### 119. `Access-Server/Antiflood-Control.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Access Server](../Access-Server.md) / Antiflood Control

[Previous](Structure-of-Directories-and-Files.md) | [Next](Priority.md)

# Antiflood Control

The antiflood control system works on [access servers](../Access-Server.md). It allows protecting the trading platform from external harmful attacks. This protection system collects the database of users who send incorrect requests to the server (e.g. attempt to authorize with an incorrect login or password), as well as users who send too often requests.

> Antiflood control works with all types of connections to the server including manager ones (via the manager terminal and Manager API).

The number of connections and incorrect request per time unit can be set up on the ["Access" (#antiflood)](../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#antiflood) tab of the access server:

!["Access" tab](images/network_add_access.png)

## System of Operation

The antiflood control system monitors user activity. Users are identified by their IP addresses as well as by the ID linked to their computers and operating systems. The following two activity types are controlled:

  * The total number of connections from one user  
The system tracks if a user creates too many connections. When a user connects to the server, their connection counter is incremented by one. If the next connection occurs in less than 3 seconds, the counter is incremented. If the specified time interval is exceeded, the counter is reset. When the counter reaches the number specified in the "Connections" field, the user is blocked for 5 minutes. The blocking period increases if the connections limit is reached again. The maximum blocking period is one hour.
  * Number of invalid packets from one user  
The system blocks brute-force attacks by analyzing authentication errors, which imply multiple login attempts with incorrect data. Also, the system detects garbage flood packets, which can be sent to the server by third-party utilities in an effort to reduce the server performance (i.e. a DoS attack). When a user sends an invalid packet to the server, the user's error counter is incremented by one. If the next invalid packet is sent in less than 5 minutes, the counter is incremented. If the specified time interval is exceeded, the counter is reset. When the counter reaches the number specified in the "Errors" field, the user is blocked for 5 minutes. The blocking period increases if the connections limit is reached again. The maximum blocking period is one hour.



The following records appear in the access server operation [Journal](../../Platform-Setup/Network-cluster/Journal.md) when a user is blocked:

  * IP is blocked after N connections [intruder] — a user is blocked by IP if the number of connections is exceeded;
  * CID is blocked after N errors [intruder] — a user is blocked by CID (computer ID) if the number of errors is exceeded.



  * It is strongly recommended to keep the antiflood control system enabled.
  * IP addresses added to the "permit always" list in the [corresponding section](../../Platform-Setup/Security/Firewall.md), are not checked by the antiflood control system.

  
---  
  
## Retrieve IP address from X-Forwarded-For

Clients can connect to the platform through public services from various proxy servers. This may happen, for example, if you use an [Anti DDoS system](../../Platform-Setup/Security/Anti-DDoS-Protection.md), such as Cloudflare. In this case, the proxy server address will be displayed for the client's IP address in [account details](../../Platform-Setup/Accounts/Editing-Account.md) and [logs](../../Platform-Setup/Network-cluster/Journal.md). The same address will be used for anti-flood control system checks. To avoid this and provide real data, you can add proxy server addresses to the [firewall](../../Platform-Setup/Security/Firewall.md) whitelist (the "always allow" rule). In this case, the access server will try to retrieve the user's real IP address from the X-Forwarded-For header provided by the proxy server upon connection.

> Please make sure the IP addresses you are adding to the whitelist belong to trusted services, which may not transmit false addresses in requests.

```

---

<a id='access-server-priority-md'></a>
### 119. `Access-Server/Priority.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Access Server](../Access-Server.md) / Priority

[Previous](Antiflood-Control.md) | [Next](../History-Server.md)

# Priority

The preference of an access server for client terminals to connect to a trade server is defined by its priority and connection quality. The lower the value if priority is, the more preferable the access server is. A [base priority (#priority)](../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#priority) (from 0 to 15) can be specified in its settings. It defines the server preference if all other conditions are equal. The final analysis of an access server is conducted upon the ping and the current priority, which depends on the basic priority and the number of current connections. Also, the quality of connection to the server is shown in the client, manager and administrator terminals based on the same data:

![The connection quality of an access point](images/access_server_preference.png)

The current priority is calculated according to the following formula: Current Priority = (Base Priority + Connections / 1000),

where:

  * Current Priority is the priority at the server current moment;
  * Base Priority is the base priority set in its [parameters (#priority)](../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#priority);
  * Connections — the number of current connections.



Every 1000 client connections increase the current priority of a server by one. The value of the current priority of access servers is available on the ["Network"](../../Platform-Setup/Network-cluster.md) tab.

```

---

<a id='access-server-structure-of-directories-and-files-md'></a>
### 119. `Access-Server/Structure-of-Directories-and-Files.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Access Server](../Access-Server.md) / Structure of Directories and Files

[Previous](../Access-Server.md) | [Next](Antiflood-Control.md)

# Structure of Directories and Files

The access server is installed to folder "access_server". This folder contains the following executable files:

  * mt5srvupdater64.exe — the executable file of the live update system of the access server;
  * mt5access64.exe — the executable file of the access server.



The main directory of the access server contains five folders: bases, config, history, liveupdate, logs.

The bases directory contains the news databases, as well as data on the server performance.

Files | Description  
---|---  
performance\ | Monthly access server performance databases and data indexes, which are displayed on the [Monitoring](../../Platform-Setup/Network-cluster/Monitor.md) tab.  
news.dat | Database of news sent to clients.  
news.idx | The index file of the news database.  
performance.dat | Data about the access server performance that are displayed on the ["Monitor"](../../Platform-Setup/Network-cluster/Monitor.md) tab are written to this file.  
  
The config directory contains configuration files:

Files | Description  
---|---  
server.ini | Individual settings of the access server.  
servers.ini | Settings of the internal [network of servers](../../Platform-Setup/Network-cluster.md).  
symbols.ini | Configurations of [symbols](../../Platform-Setup/Symbols/Symbol-Settings.md).  
time.ini | [Time](../../Platform-Setup/Time.md) settings.  
  
The history directory contains the base of history data by symbols, which was received from the history server:

Files and folders | Files | Description  
[2 chars]\\[symbol]\ | yyyy.hsc | Minute data for the symbol, divided by years. '2 chars' are the first two characters in the instrument name; 'symbol' is the name of the instrument. Arranging symbol data in different directories reduces the load on the file system and provides faster data operations.  
[2 chars]\\[symbol]\ | yyyy.tkc | Tick data for the symbol, divided by years. '2 chars' are the first two characters in the instrument name; 'symbol' is the name of the instrument. Arranging symbol data in different directories reduces the load on the file system and provides faster data operations.  
tickers.dat |  | Data by tickers.  
  
The liveupdate directory contains the latest updates of the client, manager and administrator terminals:

Files | Description  
---|---  
mt5adm.build | Live update of the administrator terminal. The build number is specified after the point.  
mt5clw.build | Live update of the client terminal.  
mt5ckwide.build | Live Update of MetaEditor.  
mt5clwmql.build | Live Update of the MQL5 compiler.  
mt5man.build | Live update of the manager terminal.  
  
The logs directory keeps files of the access server operation journal, as well crash logs:

Files and folders | Description  
---|---  
Crash\crash.log.* | The /crash directory contains server crash files. These files are automatically sent to the software developing company for detecting reasons of the crash and eliminating them.  
yyyymmdd.log | [Journal](../../Platform-Setup/Network-cluster/Journal.md) files that contain all the information about events that occur on the access server. Server logs are stored in separate files for each working day. Here yyyy — year, mm — month, dd — day.   
mt5srvupdater.log | Journal files of the platform [updates](../../Platform-Setup/Live-Update.md).

```

---

<a id='backup-server-backup-features-md'></a>
### 119. `Backup-Server/Backup-Features.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Backup Server](../Backup-Server.md) / Backup Features

[Previous](../Backup-Server.md) | [Next](Switching-to.md)

<a id="backup-features"></a>
# Backup Features (#backup-features)

All critical trade and history server data is backed up in real time. Some non-critical trade server data, as well as history server data are backed up every hour. Critical and non-critical data are displayed in the table below:

Data | Trade server | History server  
Critical (real time backup) | User base Order base Deal base Configuration databases | Trade execution base (executions) and custom settings (settings.dat) of running gateways Tick flow  
Non-critical (backup every hour) | mt5sendmail64.exe and mt5trade64.exe files Plugins (DLL, INI, DAT files including subdirectories) Reports (DLL, INI files without subdirectories) Templates (HTML, HTM files without subdirectories) | mt5history(64).exe file Gateways and data feeds (EXE, DLL, INI, DAT, JAR, CMD, BAT, PS1,VBS and PY files including subdirectories) Plugins (DLL, INI, DAT files including subdirectories)  
User directories and files specified in the [Folders (#folders)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#folders) section in backup server settings  
Non-critical (backup every five hours) | Archive databases Mail database Daily report database | Minute bar history  
Non-critical (backup every 24 hours) |  | Tick history  
  
The installation directory of the backup server contains the same folders as the server, whose backups it creates, except for the logs folder that contains the journal entries and crash logs of the backup server itself. In addition, the following executable files are available in the directory:

  * mt5srvupdater64.exe — the executable file of the live update system of the backup server;
  * mt5backup64.exe — the executable file of the backup server.



<a id="file"></a>
## Periodic file backup (#file)

Apart from synchronizing with the main server in real time, the backup server creates database file copies on the disk for certain points in time. The path for saving files and the creation time are set in the [backup server settings (#enable-backups)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#enable-backups).

To save time and disk space, backups are performed incrementally:

  * The first copy is made for all data of the backed up server. That copy is placed to ["[Backups path (#enable-backups)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#enable-backups)"]\base\\. The folder and file structure there fully matches the one of the backed up server.
  * Each subsequent day (hour of 4 hours, depending on the "[Additional backups (#archive-backup-period)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#archive-backup-period)"), an incremental copy of the data is created. Such a copy contains only the changes as compared to the first (base) copy. Such copies are placed to ["[Backups path (#enable-backups)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#enable-backups)"]\\[YYYY.MM.DD_HH.MM.SS]\\.



Thus, the server does not need to copy all the data during each backup.

Let us consider an example with a trade database. Backup was enabled on 2019.11.06. The server created a database copy on this day. It is shown on the left in the figure below. The entire history of deals is contained under the 'base' directory. It is divided by months and is presented as ZIP files. During the next day, traders performed deals through the platform, as well as the administrator edited a trade which was executed in January 2019. The next day, the backup server created an incremental copy in the catalog 2019.11.07_17.10.00 (on the right). You can see that only two ZIP archives are included in the incremental copy directory, i.e. those which have changed relative to the base copy:

![Trade database backup example: base copy and incremental copy](images/backup_base_increment.png)

The server is able to automatically delete old copies to ensure that the backups do not take up all the free disk space over time. The storage depth is set by the "[Keep backups (#enable-backups)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#enable-backups)" parameter in the backup server settings. When deleting an old backup copy, it is preliminarily applied to the main one. In fact, its files are combined with the files from the "base" directory. After that, the "base" directory will have the same status as the databases on the server at the time of creation of the deleted incremental copy. Subsequent incremental copies will already be created relative to the new base copy. This approach also reduces the amount of data copied during backup.

Let us consider this procedure using the previous example. Suppose, the "Keep backups" parameter is set to "3 days".

  * The backup was enabled on 2019.11.06 and the server created a backup copy ("base" folder). the following three days, the server was creating incremental copies in separated directories.
  * On 2019.11.11, when it is time to create the next copy, the server copies data from the incremental archive of 2019.11.07 into the base copy.



![Before deletion, the incremental copy is merged with the base copy](images/backup_base_increment_merge_1.png)

Then, the incremental archive of 2019.11.07 is deleted, while the incremental archive dated 2019.11.11 is created based on the updated base copy:

![The old incremental copy is deleted, the new one is created based on the updated base copy](images/backup_base_increment_merge_2.png)

> In addition to backup copies, the server saves the "mt5backupinfo.txt" file under the directory [backup server installation directory]\base\\. The file contains backup service information. Do not delete or modify this file. The file is not required for [database recovery (#restore)](Backup-Features.md#restore), so there is no need to copy it.

The ["Enable backups" (#enable-backups)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#enable-backups) parameter allows you to completely disable creating backup copies on the disk. The backup server status synchronization with the main one is not disabled. The backup server still remains its full copy. Disabling creation of copies on the disk may be needed if the backup server is used only to [export data to SQL](SQL-Export.md).

<a id="working-with-file-copies"></a>
### Working with file copies (#working-with-file-copies)

If you want to save the database status as of a certain point in time (for example, in order to move it to the long-term archive on another server), simply copy the basic and incremental copies for the desired date. Together, they represent the complete database status of the backed up server as of the certain point in time.

To request data from a file copy, go to the necessary section of MetaTrader 5 Administrator ([Orders (#backup)](../../Platform-Setup/Orders.md#backup), [Deals (#backup)](../../Platform-Setup/Deals.md#backup), [Positions (#backup)](../../Platform-Setup/Positions.md#backup), [Accounts](../../Platform-Setup/Accounts/Archive-and-Backup-Bases.md)) and select a copy for the desired date in the query line. The terminal collects and presents data from the basic and selected incremental copies. Such requests actually restore the state of the database as at the selected point in time.

<a id="restore"></a>
### Database recovery for a specific date (#restore)

To restore server databases as on a specific date, stop all the servers within the cluster. Next, unzip and copy the necessary databases from the \base\ directory of the backup server to the corresponding directories of the primary server.

![Unzip and copy files from the 'base' directory to the main server](images/backup_restore_base.png)

Then unzip and copy the required data from the incremental copy directory for the desired date (its format is [YYYY.MM.DD_HH.MM.SS]) to the relevant directories of the main server.

![Unzip and copy files from the incremental copy to the main server](images/backup_restore_increment.png)

> It is not recommended to restore trading databases separately. Orders, deals and positions are interrelated and should match each other.

<a id="journal"></a>
## Moving the current day logs (#journal)

The backup server is a copy of the backed up one since it stores the same data and features the same file and directory structure. In particular, it stores its logs in directories and files with the same names (Logs\*.log)

The special mechanism prevents mixing of the both servers' current day logs when [switching to the backup server](Switching-to.md).

When switching the servers, the current day log file of the previous backed up server is renamed by adding the .failover extension to its name. The backup server to replace it starts keeping the current day log from scratch. The *.failover file is generated only at the previous backed up server. The server, to which the switching is performed, simply creates its log file from scratch.

If a reverse switching is performed the same day, the .failover file is renamed back to .log and the backup server goes on keeping the log in it.

Let's consider an example of switching the main trade server to the backup one and vice versa.

Contents of \MainTrade\logs\ | Contents of \Backup\logs\  
---|---  
Current day log: 20170330.log  
  
first entry: 10:56:16.265 Startup service start initialized   
last entry: 10:57:55.421 Exit shutdown finished | Current day log: 20170330.log  
  
first entry: 10:56:16.265 Startup service start initialized   
last entry: 10:56:17.888 192.168.0.131 Config: network config synchronized  
Switching the servers, the backup server is active here now | Switching the servers, the trade server is active here now  
The previous trade server log is renamed to 20170330.log.failover:  
  
first entry: 10:56:16.265 Startup service start initialized   
last entry: 10:57:55.421 Exit shutdown finished  
The new file of the backup server log: 20170330.log  
  
first entry: 10:57:52.507 Startup service start initialized   
last entry: 10:57:55.401 192.168.0.131 Config: network config synchronized | The new file of the trade server log 20170330.log:  
  
first entry: 10:57:52.507 Startup service start initialized   
last entry: 11:02:28.433 Exit shutdown finished  
  
  
Reverse switching, the trade server is active here again | Reverse switching, the backup server is active here again  
20170330.log.failover is renamed back to 20170330.log and the new trade server entries are added to it:  
  
first entry: 10:56:16.265 Startup service start initialized   
10:57:55.421 Exit shutdown finished   
11:02:25.454 Startup service start initialized   
last entry: 11:04:01.157 192.168.0.131 Config: network config synchronized | The previous trade server log is renamed to 20170330.log.failover:  
  
first entry: 10:57:52.507 Startup service start initialized   
last entry: 11:02:28.433 Exit shutdown finished  
The backup server resumes adding entries in its former 20170330.log file:  
  
first entry: 10:56:16.265 Startup service start initialized   
last entry: 11:04:01.157 192.168.0.131 Config: network config synchronized  
  
<a id="emergency-situations-during-the-backup-process"></a>
## Emergency Situations During the Backup Process (#emergency-situations-during-the-backup-process)

Creation of backup copies by the server can be tracked by its [journal](../../Platform-Setup/Network-cluster/Journal.md). This section contains examples of journal entries describing emergency situations during backup.

2012.06.13 17:19:57 TradeOrders: invalid index header timestamp  
---  
  
Such a journal entry means that orders base index (order.idx) does not correspond to the orders base data (order.dat). A possible reason for such entry may be a backup server abnormal shutdown (for example, power cut or server manual shutdown).

This situation is not dangerous. The backup server will reconstruct the index and continue its operation. The data in the database remains fully intact. However, the reason of the abnormal server shutdown should be found out.

2012.06.13 17:19:57 TradeDeals: deals_2012.06.dat: base has invalid hash  
---  
  
This entry indicates that the deals base on a backup server differs from the one on a trading server after synchronization. In this case, the backup server will remove the indicated base and synchronize it again.

Such backup server journal entries are permissible for deals base (deals_*) after weekends (when databases optimization compaction are performed on the main server). The reason is that a backup server cannot always synchronize a month deals base in saving mode (delete the entries that were deleted during a trading server optimization) after optimizing the base on a trading server. In that case, the backup server performs the full database synchronization.

For the rest of the databases such a situation is not acceptable in any time.

```

---

<a id='backup-server-restoring-server-md'></a>
### 119. `Backup-Server/Restoring-Server.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Backup Server](../Backup-Server.md) / Restoring Server

[Previous](Switching-to.md) | [Next](SQL-Export.md)

# Restoring Server

If the main trade server fails, you will not be able to switch to the backup server manually using the MetaTrader 5 Administrator, because you will not be able to connect to the server. Managing other cluster components will also be impossible. The system of [automatic switching to the backup server (#auto)](Switching-to.md#auto) allows avoiding such a situation. However, if the system was not enabled, you will need to recover the server manually:

1\. Go to the computer where the main trade server is installed, and stop the system service if it runs. The default name of the main trade server service is mt5tmsrv. It can be stopped in the Control Panel — Administrative Tools — Services, as well as using the command line:

net stop mt5tmsrv   
or   
D:\MetaTrader 5 Platform\Main Trade\mt5trade64.exe /stop.  
---  
  
If the computer is down (is unavailable), skip this step. However, once the computer is back up, please make sure that the old trade server service has not been restarted.

2\. Go to the computer where the backup server is installed, and stop the system service. The default name of the backup server service is mt5bsrv. It can also be stopped using the Control Panel or the command line:

net stop mt5bsrv   
or   
D:\MetaTrader 5 Platform\Backup Main Trade\mt5backup64.exe /stop.  
---  
  
3\. Run the backup server file from the command line with the /gui parameter. For example:

D:\MetaTrader 5 Platform\Backup Main Trade\mt5backup64.exe /gui.  
---  
  
Click Restore in the window that appears.

![Server Configuration](images/backup_server_gui.png)

After that, the recovery process is started. Other components of the cluster will automatically switch to the new main server.

![Restoring Main Trade Server](images/restore_main_server.png)

The process of restoring is run automatically in several steps:

  * Configuring Main Trader Server  
At this stage, the IP address and port of the main server are replaced with those of the backup server, which are displayed in the upper part of the window. [The password and identifier (#identifier)](../../Platform-Setup/Network-cluster/Configuring-Servers.md#identifier) are not changed.
  * Installing Main Trade Server service
  * Uninstalling Backup Server service
  * Starting Main Trade Server service



  * Before you launch the backup server, make sure the main server is stopped. Otherwise, your clients may start working with different servers. For example, your main server and access server are located at the same provider. The provider has issues with the internet connection and the servers became unavailable. The backup server is deployed in this case. After a while, connection to the main server is restored causing two servers to work simultaneously. In this case, contact your provider and request the immediate disabling of the main server.


  * If one of the stages cannot be completed, all the changes made during restoring will be rolled back.
  * As soon as restoring is finished, it is recommended to setup a new [backup server](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md).

  
---  
  
After the recovery of the main trade server, you will be able to connect to the cluster via MetaTrader 5 Administrator. Other components can be switched to backup servers in a regular way through the interface. For example, if the history server was installed on the same machine, you can switch to the backup server by running the appropriate command in its context menu.

The described procedure can also be used to restore other servers, including additional trade servers and history server. When restoring servers, new configuration data will be sent to the main trade server. A restored server will connect to the cluster without additional settings, and you will be able to control it via MetaTrader 5 Administrator.

![Restoring History Server](images/restore_history_server.png)

```

---

<a id='backup-server-sql-export-md'></a>
### 119. `Backup-Server/SQL-Export.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Backup Server](../Backup-Server.md) / SQL Export

[Previous](Restoring-Server.md) | [Next](SQL-Export/Installation-and-Setup-of-MySQL.md)

# SQL Export

The MetaTrader 5 trading platform provides standard options for the real-time data export to MySQL, Microsoft SQL Server, FireBird, Oracle, MariaDB and PostgreSQL databases. This option enables the quick and easy deployment of data export to an external DBMS for using the platform data in any popular programming language and third-party applications. Thus, it is possible to create an intermediate layer between a trade server and broker's program services that regularly access trading data. This reduces the load on the trade server when it receives the current trading data.

The export function is enabled by simple specification of [settings for connection to DBMS (#sql)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql) via MetaTrader 5 Administrator. After that, the backup server will immediately perform an initial synchronization of data from the DBMS. Further, new data will be exported to the DBMS in real time. The following data is exported:

  * Information about clients (general information and trading status)
  * Current active orders and positions
  * The history of orders and deals
  * Current prices
  * Virtually all settings of the trading platform (except for the working time, synchronization and spreads)



The description of installation and setup of popular databases is provided in appropriate subsections:

  * [MySQL Server 5.7](SQL-Export/Installation-and-Setup-of-MySQL.md) (supported versions: 5.1, 5.5, 5.6, 5.7, 8.0, 8.1)
  * [MariaDB 10.2](SQL-Export/Installation-and-Setup-of-MariaDB.md) (all version supported)
  * [Microsoft SQL Express 2012](SQL-Export/Installation-and-Setup-of-MS-SQL.md) (supported versions: 2005, 2008, 2008 R2, 2012, 2014, 2016, 2017, 2019, 2022)
  * [Oracle Database Express Edition 11g](SQL-Export/Installation-and-Setup-of-Oracle.md) (supported versions: 11g/11g Express Edition, 12c, 18c, 19c, 21c, 23ai)
  * [PostgreSQL](SQL-Export/Installation-and-Setup-of-PostgreSQL.md) (supported versions: 8.4 — 17)



## Operation Principle

Export mechanism has been implemented on the side of backup servers replicating data from the trade servers.

Below are the general steps of synchronization in a backup server:

  * The backup server connects to the appropriate trade server and is synchronized with it.
  * After synchronization with the trade server is successfully complete, the backup server synchronizes an external DBMS.
  * The backup server applies changes to its databases and the external DBMS via transactions from the trade server.



The backup server performs initial synchronization based on time stamps (Timestamp field in the tables) during each connection to DBMS:

  * All logs with different time stamps in the external DBMS are replaced with backup server logs.
  * All entries that are absent at the backup server are removed from the external DBMS.



> A time stamp is used for checking the identity of the backup and the external DBMS logs. If a time stamp on the backup is similar to the on at the external DBMS, a backup server considers that all other log fields are similar and the log update is not required.

After databases are synchronized, the backup server applies change transactions on the external DBMS. Besides, prices and profit values for active orders (mt5_orders), positions (mt5_positions) and related trading accounts (mt5_accounts) are also periodically updated.

A detailed description of exported tables can be found in the following subsections:

  * [mt5_symbols](SQL-Export/mt5-symbols.md) — [symbols'](../../Platform-Setup/Symbols.md) configurations.
  * [mt5_symbols_sessions](SQL-Export/mt5-symbols-sessions.md) — symbols' [trade and quotation sessions](../../Platform-Setup/Symbols/Symbol-Settings/Sessions.md).
  * [mt5_groups](SQL-Export/mt5-groups.md) — [groups'](../../Platform-Setup/Groups.md) configurations.
  * [mt5_groups_symbols](SQL-Export/mt5-groups-symbols.md) — individual [symbol settings for groups](../../Platform-Setup/Groups/Group-Symbol-Settings.md).
  * [mt5_commissions](SQL-Export/mt5-commissions.md) — [commission](../../Platform-Setup/Groups/Commission-Settings.md) settings for groups.
  * [mt5_commissions_tiers](SQL-Export/mt5-commissions-tiers.md) — [commission level (#level)](../../Platform-Setup/Groups/Commission-Settings.md#level) settings.
  * [mt5_managers](SQL-Export/mt5-managers.md) — [manager](../../Platform-Setup/Managers.md) accounts.
  * [mt5_clients](SQL-Export/mt5-clients.md) — [client](../../Platform-Setup/Clients.md) database.
  * [mt5_documents](SQL-Export/mt5-documents.md) — database of [client documents (#documents)](../../Platform-Setup/Clients.md#documents).
  * [mt5_users](SQL-Export/mt5-users.md) — [account](../../Platform-Setup/Accounts.md) database.
  * [mt5_orders](SQL-Export/mt5-orders.md) — open [order](../../Platform-Setup/Orders.md) database.
  * [mt5_positions](SQL-Export/mt5-positions.md) — [position](../../Platform-Setup/Positions.md) database.
  * [mt5_orders_history](SQL-Export/mt5-orders-history.md) — closed [order](../../Platform-Setup/Orders.md) database.
  * [mt5_deals](SQL-Export/mt5-deals.md) — [deal](../../Platform-Setup/Deals.md) database.
  * [mt5_accounts](SQL-Export/mt5-accounts.md) — trade account state database.
  * [mt5_prices](SQL-Export/mt5-prices.md) — database of prices.
  * [mt5_daily](SQL-Export/mt5-daily.md) — database of daily reports.


  * [mt5_daily_orders](SQL-Export/mt5-daily-orders.md) — data on the status of open orders at the end of the trading day.
  * [mt5_daily_positions](SQL-Export/mt5-daily-positions.md) — data on the status of position at the end of the trading day.


  * [mt5_holidays](SQL-Export/mt5-holidays.md) — [holiday](../../Platform-Setup/Holidays.md) configurations.
  * [mt5_network](SQL-Export/mt5-network.md) — general [settings of servers](../../Platform-Setup/Network-cluster/Configuring-Servers.md).
  * [mt5_network_access_servers](SQL-Export/mt5-network-access-servers.md) — access servers settings.
  * [mt5_network_history_servers](SQL-Export/mt5-network-history-servers.md) — history server settings.
  * [mt5_network_trade_servers](SQL-Export/mt5-network-trade-servers.md) — trade servers settings.
  * [mt5_network_backup_servers](SQL-Export/mt5-network-backup-servers.md) — backup servers settings.
  * [mt5_network_backup_folders](SQL-Export/mt5-network-backup-folders.md) — backed up custom folders.
  * [mt5_firewall](SQL-Export/mt5-firewall.md) — [firewall](../../Platform-Setup/Security/Firewall.md) settings.
  * [mt5_routing](SQL-Export/mt5-routing.md) — settings of [routing rules](../../Platform-Setup/Routing.md).
  * [mt5_routing_dealers](SQL-Export/mt5-routing-dealers.md) — settings of [dealers/gateways (#dealers)](../../Platform-Setup/Routing.md#dealers) in routing rules.
  * [mt5_routing_conds](SQL-Export/mt5-routing-conds.md) — [additional conditions (#condition)](../../Platform-Setup/Routing/Actions-and-Conditions.md#condition) in routing rules
  * [mt5_feeders](SQL-Export/mt5-feeders.md) — settings of [data feeds](../../Platform-Setup/Data-Feeds.md).
  * [mt5_feeder_translates](SQL-Export/mt5-feeder-translates.md) — [conversion settings (#translation)](../../Platform-Setup/Data-Feeds/Configuration-of.md#translation) on data feeds.
  * [mt5_feeder_params](SQL-Export/mt5-feeder-params.md) — [additional settings (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) of data feeds.


  * [mt5_feeder_symbols](SQL-Export/mt5-feeder-symbols.md) — [symbol settings (#symbols)](../../Platform-Setup/Data-Feeds/Configuration-of.md#symbols) for data feeds.


  * [mt5_reports](SQL-Export/mt5-reports.md) — [report](../../Platform-Setup/Reports.md) settings.
  * [mt5_report_params](SQL-Export/mt5-report-params.md) — [additional settings (#module)](../../Platform-Setup/Reports.md#module) of reports.
  * [mt5_plugins](SQL-Export/mt5-plugins.md) — [plugin](../../Platform-Setup/Plugins.md) settings
  * [mt5_plugin_params](SQL-Export/mt5-plugin-params.md) — [additional settings (#module)](../../Platform-Setup/Plugins.md#module) of plugins.
  * [mt5_time](SQL-Export/mt5-time.md) — platform [trading time settings](../../Platform-Setup/Time.md).
  * [mt5_time_weekdays](SQL-Export/mt5-time-weekdays.md) — [working time schedule (#daily-settings)](../../Platform-Setup/Time.md#daily-settings) of the platform, by days.
  * [mt5_gateways](SQL-Export/mt5-gateways.md) — gateway settings.
  * [mt5_gateways_params](SQL-Export/mt5-gateways-params.md) — additional gateway settings.
  * [mt5_gateways_translates](SQL-Export/mt5-gateways-translates.md) — translation settings in gateways.


  * [mt5_gateways_symbols](SQL-Export/mt5-gateways-symbols.md) — [symbol settings (#symbols)](../../Platform-Setup/Gateways/Configuration-of.md#symbols) for gateways.



## Your own data in MetaTrader 5 tables

In the platform, you can create your own tables and databases, add your own fields in mt5_* tables, which are used for data export, as well as create stored procedures and triggers.

  * The backup server does not recreate data, but only adds or updates existing records. A table entry is only deleted if the appropriate entry is deleted on the platform side. For example, if a user is added to the mt5_users tables, the appropriate user record will exist in the database until the user is deleted from MetaTrader 5.
  * The backup server only works with its own tables and fields.
  * The backup server does not create default indexes. Each index is an extra load on the database, which can slow down exports and information updates.
  * When you create your own fields in mt5_* tables, do not forget to set default values for them (or allow NULL). Otherwise, the backup server will not be able to add new entries to the tables.



## Additional information

Find additional recommendations on handling SQL databases in the articles:

  * [Export to SQL database takes too much time](https://support.metaquotes.net/en/articles/1598)
  * [How to present account permissions in MySQL](https://support.metaquotes.net/en/articles/1576)



```

---

<a id='backup-server-switching-to-md'></a>
### 119. `Backup-Server/Switching-to.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Backup Server](../Backup-Server.md) / Switching to

[Previous](Backup-Features.md) | [Next](Restoring-Server.md)

<a id="switching-to-backup-server"></a>
# Switching to Backup Server (#switching-to-backup-server)

The MetaTrader 5 platform can automatically monitor the availability of trade and history servers. The monitoring is performed by the backup server itself as well as by access servers. Each server monitors the availability of the main server and polls other monitoring servers to check whether the main server is available to them.

If the main server is unavailable for some time, the platform will automatically switch to the backup server. The downtime is minimal, while switching usually takes less than a minute.

In the platform, you can also [switch to a backup server manually (#manual)](Switching-to.md#manual). In case of a failure of the history server or a non-main trade server, you can quickly switch to the backup server in the automated mode. The same procedure provides for an easy migration of servers to new hardware. You will only need to properly setup the backup server via MetaTrader 5 Administrator, use the [fast deployment](../../Platform-Installation/Fast-Deployment.md) procedure and switch to the newly installed backup server afterwards.

> [All critical trade and history server data](Backup-Features.md) is backed up in real time. Some non-critical trade server data, as well as history server data are backed up every hour. When switching to the backup server, critical data obtained during the procedure may be lost (the procedure itself usually takes less than a minute). Therefore, we strongly recommend that you switch to the backup server only outside of working hours.

<a id="auto"></a>
## Switching to the Backup Server Automatically (#auto)

Automatic switching to a backup server allows minimizing the platform unavailability time in case of emergency situations. The platform automatically monitors the performance of its components and switches to backup servers if necessary.

The necessity to switch to the backup server is defined by the monitoring ("witness") servers. The backup server itself and access servers (with monitoring mode enabled) act as the monitoring ones. The backup server monitors the availability of the master server in real time mode and checks if it is available for the access servers as well.

Automatic switching can be enabled in the master server's settings (either a trade or a history one):

![Failover](images/trade_backup_settings.png)

There are two scenarios for determining the unavailability of the main server:

  * Server is not accessible to most access servers — the number of the monitoring servers unable to access the master server should exceed the ones able to access it at least by one for the switch to occur. If you have configured five monitoring servers, the main server should be unavailable to at least three of them, or to four of six monitoring servers. If you are using two monitoring servers (the minimum allowed number), the main server should be unavailable for both of them.
  * Server is not accessible to all access servers — the master server should be unavailable for all monitoring servers for the switch to occur.If you have configured five monitoring servers, the main server should be unavailable to all of them.



If several backup servers are used for one main server, then each of the backup servers will start switching to the master server mode in case of the main server failure. The last switched server will be used as the main server, while all the rest of them will switch back to backup mode.

If a certain backup server should not be used for automatic switching, disable in its settings the following option: ["Use this backup server for failover" (#failover)](../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#failover). This may be needed if the backup server is used only for [exporting data to SQL database](SQL-Export.md).

  * The number of monitoring servers should not be less than 2.
  * It is recommended to install access servers on different computers (different data centers), separate from the main and history servers. This will provide the most relevant server monitoring data.

  
---  
  
In "Switch timeout" parameter, you can specify the time (in seconds) during which the server should be unavailable for monitoring servers to start switching to the back-up server. Also, after this time period, other platform components start their attempts to connect to the [access points (#network)](../../Platform-Setup/Network-cluster/Configuring-Servers.md#network) of the current backup server (trying to connect to it as to the master one).

> When measuring the time of the master server's unavailability, its cause is considered. In case of a manual restart of the server, the unavailability time is increased according to the time required for restart.

To make an access server a monitoring one, enable "Use this server for monitoring the cluster and failover" option in the server's settings:

![Access server settings](images/network_add_access.png)

  * If the access server is unavailable for the backup one, that does not mean that the master server is also unavailable. In this case, the number of monitoring servers is reduced.


  * In case of the master and other servers' simultaneous failure, the master server is restored first.

  
---  
  
<a id="features-of-connecting-to-monitoring-servers"></a>
### Features of Connecting to Monitoring Servers (#features-of-connecting-to-monitoring-servers)

The backup server uses the following algorithm for connecting to the monitoring servers:

  * As soon as the main server becomes unavailable for the backup server, the backup server checks all monitoring servers one by one and trues to connect to them.
  * First, the backup server tries to connect to the monitoring server via the local address if available. Connection to a local address is performed if [listen addresses (#bind)](../../Platform-Setup/Network-cluster/Configuring-Servers.md#bind) of the backup and access servers are located in 10.*, 172.16.* — 172.31.* or 192.168* subnet. The first three octets in their addresses should coincide. In that case, both servers are deemed to be located in a single subnet, and the backup server tries to connect directly to the listen address of the access server. Example: the backup server has 192.168.0.100:1951 listen address, while the access one - 192.168.0.105:1950.
  * If connection via the local address has failed, the backup server uses [public points (#public)](../../Platform-Setup/Network-cluster/Configuring-Servers.md#public) of the access server.



> In order for the switch to occur as fast as possible, all access servers should be available. There should be no disabled servers among the monitoring ones. The backup server spends 5 seconds trying to connect to a non-existent address.

<a id="using-several-backup-servers"></a>
### Using Several Backup Servers (#using-several-backup-servers)

If several backup servers are used for a single main one, then each of the backup servers starts switching to the master server mode in case of the main server's failure. The last switched server is used as the master one, while all the rest of them switch back to backup server mode.

<a id="logging-monitoring-results"></a>
### Logging Monitoring Results (#logging-monitoring-results)

You can request the backup server's log using "Failover" keyword to control the process of monitoring the master server. Sample entries:

2013.09.09 09:07:33 Failover master server '1' - 'Trade Main' is available  
2013.09.09 09:07:33 Failover master server '1' - 'Trade Main' is available for witness server '2' - 'Access Point 1'  
2013.09.09 09:07:34 Failover master server '1' - 'Trade Main' is available for witness server '6' - 'Access Point 2'  
2013.09.09 09:07:54 Failover witness access server '7' is not available  
2013.09.09 09:07:54 Failover master server '1' - 'Trade Main' is available for witness server '11' - 'Access Point 3  
2013.09.09 09:07:54 Failover master server '1' - 'Trade Main' is available for 4 witnesses and unavailable for 0 witnesses [0 min]  
---  
  
These entries mean as follows:

  * Master server with identifier 1 is available.
  * Master server with identifier 1 is available for monitoring server 2 named Access Point 1.
  * Master server with identifier 1 is available for monitoring server 6 named Access Point 2.
  * Monitoring server with identifier 7 is unavailable for the backup server.
  * Master server with identifier 1 is available for monitoring server 11 named Access Point 3.
  * Master server is available for 4 witnesses and not available to 0 witnesses. The time, during which the server has been unavailable, is shown in brackets.



<a id="working-after-switching-to-the-backup-server"></a>
### Working after Switching to the Backup Server (#working-after-switching-to-the-backup-server)

After the backup server has switched to the trading one, the client terminals scan public access points of the access server in order to connect to it. The time of going through the access points depends on the following factors:

  * Actual accessibility of the public point for a client. If an address is not available for the client (for example, a local IP address is specified in the settings as a public access point), the terminal spends 10 seconds trying to connect to it. An attempt to connect to the next access point is made only in 10 seconds.
  * The number of the access server addresses unavailable for clients. For example, if two local addresses 192.168.0.100 and 192.168.0.101, as well as an external one - access.server.com (available external address of the server) are specified among the public access points, the client terminals will first spend 20 seconds trying to connect to local addresses before successfully connecting to the external one.
  * Availability of the trade and history servers for the access one. The access server goes through the access points of the trade and history servers according to their [network settings (#network)](../../Platform-Setup/Network-cluster/Configuring-Servers.md#network). Correctness of the network settings defines how quickly the access server becomes ready for work.



> It is recommended that the access servers having local IP addresses in the list of [public points (#public)](../../Platform-Setup/Network-cluster/Configuring-Servers.md#public) are made available only for the administrators and managers working in the same local network. To do this, uncheck all options except "Allow administrator connection" and "Allow manager connection" ones in the [Permissions (#permissions)](../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#permissions) tab of the access server.

<a id="manual"></a>
## Manual Switching to a Backup Server and Migration of Servers (#manual)

In the platform, it is possible switch to a backup server from the main one manually. It is a quick and automatic procedure. In addition to emergency cases, the procedure can be used for migrating servers to new hardware.

Install the backup server on the computer, to which you plan to migrate the server. After installing and launching the backup server, it is recommended to let it operate for a few days on the new machine to make sure it operates well.

  * If you want to avoid the loss of data that is backed up every hour, the backup server should be restarted before switching to it. The server creates the latest data backup. While the server is busy backing up data, the following sign is displayed on its icon ![Backup in process](images/backup_server_backuping_icon.png) (the icon itself has the following look ![Backup in process](images/backup_server_backuping_icon2.png)). Start switching to the backup server only after the backup process is complete.
  * Server migration must only be performed in non-trading hours. During the switching procedure, the main server continues to receive data, which will not be copied to the backup server.
  * In order to prevent important information from being lost, trading and changes in the client base are not allowed on the main server right after the start of switching to the backup server. The ban is valid for one minute. If the platform fails to switch to a backup server within this period, the ban is removed.

  
---  
  
Execute "![Switch to backup server](images/switch_to_bakcup_icon.png) Switch to backup server" command:

![Switching to the backup server](images/switching_to_backup.png)

To avoid accidental switching, the platform requires an additional confirmation. In the dialog that appears, enter the required characters and click "Switch".

![Confirming the switching to the backup server](images/switch_to_backup_confirm.png)

After the procedure is complete, you will see that the trade/history server has changed places with the backup server in Network section.

<a id="features"></a>
## The Features of the Switching Procedure (#features)

On the backup server's side, the switching process is performed as follows:

  * The backup server stops Windows service.
  * It also updates the network settings of the platform. The servers exchange roles, while the main server becomes the backup one, and the backup server starts operating as the main trade server:


  *     * The network settings (IP addresses, outgoing address, public points) and the name of the former backup server are set for the main server in the platform configuration.
    * The IP address and the name of the former main server are set for the backup server in the platform configuration.
    * On the servers, only their internal IDs change. The ID of the former main server is set for the new backup server, and the ID of the former backup server is set for the new main one.



![Changes in the Platform Configuration](images/switch_to_backup_server_change.png)

  * The master server's Windows service is installed
  * Notification is sent to the master server, waiting for confirmation.
  * The master server's Windows service is launched.
  * The former backup server's Windows service is deleted.



If the backup server has been active during the switch, it is switched to the backup mode:

  * The master server's Windows service is stopped.
  * Network settings are updated similar to how it is done for the backup server.
  * The backup server's Windows service is installed and launched.
  * The former master server's Windows service is deleted.



  * If the former master server was inactive during the switch to the backup one (for example, the server computer was shut down) and the copy restored from backup is already working by the moment the server is restored, the former master server switches to the backup mode automatically (unless switching to a backup server is prohibited in its [settings (#backup)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#backup)).


  * Physically (on the hard drive), the new trade/history server operates from the former backup server's directory, while the new backup server operates from the trade/history server's one.

  
---

```

---

<a id='backup-server-sql-export-installation-and-setup-of-ms-sql-md'></a>
### 119. `Backup-Server/SQL-Export/Installation-and-Setup-of-MS-SQL.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / Installation and Setup of MS SQL

[Previous](Installation-and-Setup-of-MariaDB.md) | [Next](Installation-and-Setup-of-Oracle.md)

# Installation and Setup of Microsoft SQL Server

Download one of the distribution kits from Microsoft website ([http://www.microsoft.com/en-us/download/details.aspx?id=29062](https://www.microsoft.com/en-us/download/details.aspx?id=29062)) to install free version of Microsoft SQL Exress 2012.

You need to download ENU\x86\SQLEXPR_x86_ENU.exe or ENU\x64\SQLEXPR_x64_ENU.exe.

  * MetaTrader 5 supports data export both to Microsoft SQL Server 2005/2008/2012/2014/2016/2017/2019/2022 and to their Express versions.
  * Microsoft SQL Server Express 2005 has a limit of 4 GB on user data. Microsoft SQL Server Express 2008 R2 / 2012 has a limit of 10 GB. Therefore, it is recommended to use 2008 R2 or 2012 as Express version. If the limit is exceeded, new data will not be added to the database.


  * Operating system Windows 8 or higher is required for the [Microsoft SQL 2016](https://www.microsoft.com/en-us/download/details.aspx?id=56840) installation.


  * Select 32 or 64-bit considering potential volumes of databases. 64-bit server version is more preferable, as it makes possible to have data caches of bigger volume and has better scalability due to increasing RAM on the server.


  * By default, the backup server connects to the database using the Windows system driver MS OLE DB Provider for SQL Server (SQLOLEDB). This driver is pre-installed in all operating systems, however it is outdated and does not support the TLS 1.1 and TLS 1.2 protocols. If your company's policy does not allow using TLS protocols below 1.1. and they are disabled in the system, the SQLOLEDB driver will not be able to provide backup server connection to the database. In this case you should install an additional driver [MSOLEDBSQLS](https://www.microsoft.com/en-us/download/details.aspx?id=56730), which supports protocols TLS 1.1 and 1.2. After that the backup server will automatically start using the new driver for connecting to the database.

  
---  
  
Downloaded distribution kit should be installed in accordance with the instructions. First, select "New SQL Server stand-alone installation or add features to an existing installations" to install a new copy of Microsoft SQL Server. Check the "I accept the license terms" option at "License Terms" step. Leave default parameters at the following steps up to "Server Configuration". Set Automatic mode for "SQL Server Browser" at "Server Configuration" step:

![MSSQL_6_a](images/mssql_6_a.png)

Select "Mixed Mode (SQL Server authentication and Windows authentication)" and specify the administrator password at "Database Engine Configuration" step:

![MSSQL_8_a](images/mssql_8_a.png)

Leave default parameters at the following steps.

TCP/IP should also be enabled for access to SQL Server from the network. To do this, launch "SQL Server Configuration Manager" from the start menu:

![MSSQL_TCP](images/mssql_tcp.png)

Restart SQL Server (SQLExpress) service in SQL Server Services section.

Launch SQLCMD.exe application ("C:\Program Files (x86)\Microsoft SQL Server\110\Tools\Binn\OSQL.EXE" or "C:\Program Files (x86)\Microsoft SQL Server\110\Tools\Binn\OSQL.EXE") with the following parameters after installation to create a database:

SQLCMD.EXE -S localhost\SQLEXPRESS -U sa -P password  
---  
  
The password is the same as at "Database Engine Configuration" step. Execute the following command in SQLCMD.exe console:

CREATE DATABASE METATRADER5  
GO  
---  
  
The database will be generated.

In case backup and MS SQL servers are installed on the same computer, connection settings will be as follows:

![MSSQL_AA](images/mssql_aa.png)

In case backup and MS SQL servers are located on different computers:

![MSSQL_BA](images/mssql_ba.png)

> It is recommended to install MS SQL and backup servers on the same computer for faster export. It should also be kept in mind that the backup server itself also consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backups will work close to necessary DBMS.

Additional export parameters can be selected at [SQL Options (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) tab.

The backup server will immediately start export into the external DBMS after all settings are specified. Request the log of the appropriate backup server using SQL keyword to track the export process: 

13:24:40 SQL Export MSSQL: successfully connected to database 'mt5' at 'localhost\SQLEXPRESS' as user 'sa'  
13:24:40 SQL Export MSSQL: server version 11.0.2100.60 RTM (Express Edition)  
13:24:40 SQL Export MSSQL: table 'mt5_symbols' creating started  
13:24:40 SQL Export MSSQL: table 'mt5_symbols' created  
13:24:40 SQL Export MSSQL: primary key for 'mt5_symbols' adding started  
13:24:40 SQL Export MSSQL: primary key for 'mt5_symbols' added  
13:24:40 SQL Export MSSQL: table 'mt5_symbols_sessions' creating started  
13:24:40 SQL Export MSSQL: table 'mt5_symbols_sessions' created  
13:24:40 SQL Export MSSQL: primary key for 'mt5_symbols_sessions' adding started  
13:24:40 SQL Export MSSQL: primary key for 'mt5_symbols_sessions' added  
13:24:40 SQL Export Symbols: 0 symbols and 0 sessions loaded in 344 msecs  
13:24:40 SQL Export Symbols: synchronization started  
...  
---

```

---

<a id='backup-server-sql-export-installation-and-setup-of-mariadb-md'></a>
### 119. `Backup-Server/SQL-Export/Installation-and-Setup-of-MariaDB.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / Installation and Setup of MariaDB

[Previous](Installation-and-Setup-of-MySQL.md) | [Next](Installation-and-Setup-of-MS-SQL.md)

# Installation and Setup of MariaDB

To install MariaDB, download the required version from the official product website <https://downloads.mariadb.org/>. At the time, the platform supports all available MariaDB versions.

> Choose between 32-bit and 64-bit versions based on the evaluated potential volume of data bases. The 64-bit server version is more preferable, as it makes possible to have data caches of more than 2 Gb and has better scalability due to increasing RAM on the server.

Run the installation file and follow the on-screen instructions. The below example shows the installation of MariaDB 10.2 (x64).

![MariaDB Installation](images/mariadb_install.gif)

After selecting components for the installation (you can install with default settings), specify the password for the "root" administrator account. For security reasons, it is recommended that you do not allow the use of the "root" account during remote connections (leave the "Enable root access from remote machines" option disabled). Instead, after installing the MariaDB server and creating a scheme (database) for working with MetaTrader 5, create a separate account with access only to the desired schema, and allow remote connections to it.

It is also recommended to enable the "Use UTF8 as default server's character set" option.

Then, specify network settings (default settings can be used) and the parameter for sending anonymous reports on the DBMS operation (can be disabled). After that, start the installation process and wait for it to finish.

![MariaDB Installation](images/mariadb_install2.gif)

Now create a schema (a database) to which data from MetaTrader 5 will be exported. To do this, launch the MySQL Client (MariaDB) program from the Start menu. In the window that appears, enter the password for the "root" account and press Enter. Then enter a command to create a data base, e.g. "create schema metatrader5;". Here "metatrader5" is the name of the schema. You can use any other name.

![Creating a schema for exporting data from MetaTrader 5](images/mariadb_create_db.png)

Next, configure data export on the MetaTrader 5 side. If the backup server and the MariaDB server are installed on the same computer, the following settings will be used:

![Export settings when installing MariaDB on the same computer where the backup server is installed](images/mariadb_setting_local.png)

If the database is installed separately from the backup server, specify its address in the "Server" field. In the Login and Password fields, specify he details of the account that has access to the required schema and is allowed for use during remote connection.

![Export settings when installing MySQL on a separate computer](images/mariadb_setting_remote.png)

> It is recommended to install MariaDB and the backup server on the same computer for faster export. However, it should also be kept in mind that the backup server consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backup servers will run close to necessary DBMS. 

Additional export parameters can be selected at [SQL Options (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) tab.

```

---

<a id='backup-server-sql-export-installation-and-setup-of-mysql-md'></a>
### 119. `Backup-Server/SQL-Export/Installation-and-Setup-of-MySQL.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / Installation and Setup of MySQL

[Previous](../SQL-Export.md) | [Next](Installation-and-Setup-of-MariaDB.md)

# Installation and Setup of MySQL Server

Download one of the distribution kits from MySQL website ([http://dev.mysql.com/downloads/mysql](https://dev.mysql.com/downloads/mysql)) to start installation.

> Select 32 or 64-bit considering potential volumes of databases. 64-bit server version is more preferable, as it makes possible to have data caches of more than 2 Gb and has better scalability due to increasing RAM on the server.

Downloaded distribution kit should be installed in accordance with the instructions:

  * at the first step, agree to the terms of use and click "Next"
  * at the second step, select the installation type ("Server only" is recommended)
  * at the third step, click "Execute" and wait for the installation to complete
  * at the fourth and fifth steps, click "Next" to go to the MySQL configuration



![MySQL Installation](images/mysql_install.gif)

During the first configuration step, select the installation type "Standalone MySQL Server /Classin MySQL Replication". Next, select the type of the computer on which MySQL is installed. Based on this information, the configuration Wizard sets efficient parameters for memory, hard drive and CPU consumption. Developer Machine should not be used in real work, therefore, select one of the following types:

  * Server Machine is used in case other services (for example, web server) are present on the computer. In this case, MySQL will consume a "moderate" amount of memory.
  * Dedicated MySQL Server Machine should be selected if the computer will be used exclusively for MySQL server. In this case, MySQL will consume "maximum available" amount of memory for faster performance.



In addition to the computer type, ports and communication channels can also be configured from here, although you can use default values ​​for these parameters.

![Database Configuration](images/mysql_configure.gif)

At the next step, specify the password for the root login (administrator account). Here you can also create additional accounts and configure permissions for them.

![Configuring MySQL Accounts](images/mysql_configure_users.png)

Further you will be asked to configure the integration of the MySQL server with the operating system, as well as the server extensions. You can use default settings for the above parameters. At the last step, click "Execute" and wait for the configuration to complete.

![MySQL configuration completion](images/mysql_configure_finish.gif)

To increase MySQL server performance, edit the my.ini file located in the MySQL installation directory, i.e. C:\Program Files\MySQL\MySQL Server 5.7\my.ini for the 64-bit version and C:\Program Files (x86)\MySQL\MySQL Server 5.7\my.ini for the 64-bit version. The file can also be located in C:\Program Data\MySQL\MySQL Server 5.7.

# InnoDB, unlike MyISAM, uses a buffer pool to cache both indexes and  
# row data. The bigger you set this the less disk I/O is needed to  
# access data in tables. On a dedicated database server you may set this  
# parameter up to 80% of the machine physical memory size. Do not set it  
# too large, though, because competition of the physical memory may  
# cause paging in the operating system. Note that on 32bit systems you  
# might be limited to 2-3.5G of user level memory per process, so do not  
# set it too high.  
innodb_buffer_pool_size=2046M  
---  
  
This parameter should be selected considering the server's bit count and available physical memory:

  * for a 32-bit server this value should not exceed 80 % of physical memory and it also should not exceed 2046;
  * for a 64-bit server this value should not exceed 80 % of physical memory.



When exporting data, the platform uses zero date if a date is not specified. Thus in my.ini you need to turn off the SQL modes that prohibit zero dates: NO_ZERO_IN_DATE and NO_ZERO_DATE. Find the "sql_mode" parameter and delete that modes from it:

sql_mode = "STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION"  
---  
  
The last step is creation of the schema, to which MySQL data is exported, and performing configuration on the side of MetaTrader 5.

To do this, launch MySQL 5.7 Command Line Client in Start - All Programs - MySQL - MySQL Server 5.7 and enter root password. The following script should be executed after that:

create schema schema_name;  
---  
  
For example:

create schema metatrader5;  
---  
  
## Installation of MySQL version 8.0 and above

MySQL versions 8.0 and higher support new authentication type, which includes an improved SHA256 encryption of passwords, additional caching on the server side and a number of other new functions. The previous authentication version (Legacy) is also supported, but the new one is used by default.

The new authentication version is not supported in MetaTrader 5. To enable export of platform data to MySQL version 8.0 or higher, choose the previous authentication method "Use Legacy Authentication Method" during installation:

![Authentication type in MySQL 8.0 and above](images/mysql_8.png)

If MySQL is already installed with the new authentication method, you may switch to the Legacy method as described below. Open my.ini in C:\ProgramData\MySQL\MySQL Server 8.0\ and find the following line:

default_authentication_plugin=caching_sha2_password  
---  
  
Change the values of the parameter:

default_authentication_plugin=mysql_native_password  
---  
  
Next, change the authentication type for the user, under which you are connecting to the database. Open 'Command Line Client' and run the following command:

ALTER USER 'username'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';  
---  
  
Here 'username' is the name of the database user, and password is the new password for the user.

After that you will be able to connect to the database using the Legacy authentication method and to export data from MetaTrader 5 into it.

## Configuration on MetaTrader 5 side

In case backup and MySQL servers are installed on the same computer, connection settings will be as follows:

![Export settings when installing MySQL on the same computer where the backup server is installed](images/mysql_platform_local.png)

In case backup and MySQL servers are located on different computers:

![Export settings when installing MySQL on a separate computer](images/mysql_platform_remote.png)

> It is recommended to install MySQL and backup servers on the same computer for faster export. It should also be kept in mind that the backup server itself also consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backups will work close to necessary DBMS.

Additional export parameters can be selected at [SQL Options (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) tab.

After all settings are specified, the backup server will immediately start export into the external DBMS. Request the [journal](../../../Platform-Setup/Network-cluster/Journal.md) of the appropriate backup server using SQL keyword to track the export process:

19:00:16 SQL Export MySQL: successfully connect to '127.0.0.1:metatrader5' for 'root'  
19:00:16 SQL Export MySQL: server version 5.7.19  
19:00:16 SQL Export MySQL: table 'mt5_symbols' creating started  
19:00:16 SQL Export MySQL: table 'mt5_symbols' created  
19:00:16 SQL Export MySQL: primary key for 'mt5_symbols' adding started  
19:00:16 SQL Export MySQL: primary key for 'mt5_symbols' added  
19:00:16 SQL Export MySQL: table 'mt5_symbols_sessions' creating started  
19:00:16 SQL Export MySQL: table 'mt5_symbols_sessions' created  
19:00:16 SQL Export MySQL: primary key for 'mt5_symbols_sessions' adding started  
19:00:16 SQL Export MySQL: primary key for 'mt5_symbols_sessions' added  
19:00:16 SQL Export Symbols: 0 symbols and 0 sessions loaded in 312 msecs  
19:00:16 SQL Export Symbols: synchronization started  
...  
---

```

---

<a id='backup-server-sql-export-installation-and-setup-of-oracle-md'></a>
### 119. `Backup-Server/SQL-Export/Installation-and-Setup-of-Oracle.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / Installation and Setup of Oracle

[Previous](Installation-and-Setup-of-MS-SQL.md) | [Next](Installation-and-Setup-of-PostgreSQL.md)

# Installation and Setup of Oracle Database

Download the distribution kit from the Oracle's website ([http://www.oracle.com/technetwork/products/express-edition/downloads/index.html](https://www.oracle.com/technetwork/products/express-edition/downloads/index.html)) to install free version of Oracle Database Express Edition. Oracle allows the free use of only the 32-bit version of Express. Therefore, agree to the license terms and download Oracle Database Express Edition 11g Release 2 for Windows x32.

  * ["Update for Visual C++ 2013 and Visual C++ Redistributable Package"](https://support.microsoft.com/en-us/help/3179560/update-for-visual-c-2013-and-visual-c-redistributable-package) must be installed on the computer where the backup server is installer. Otherwise expert to Oracle databases will not be possible.


  * Oracle Database Express Edition is limited to 11 GB of user data. If the limit is exceeded, new data will not be added to the database.

  
---  
  
Distribution kit consists of a ZIP archive that should be unpacked into a temporary folder. Then launch DISK1\setup.exe and follow the instructions:

  * accept the license terms at License Agreement stage;
  * specify administrator password at Specify Database Passwords stage:



![Oracle_4](images/oracle_4.png)

Then click Next at the following stages and Install at the last one.

Create the client that will be used for connection. To do that, launch sqlplus.exe:

sqlplus.exe system/password  
---  
  
Use the same password that was specified at Specify Database Passwords stage during installation. For example:

sqlplus.exe system/MyAdminPassword  
---  
  
Then execute the following command to create the user:

create user user_name identified by password default tablespace users temporary tablespace temp;  
---  
  
And allow connection for it:

grant connect,resource to user_name;  
---  
  
For example:

create user mt5user identified by mt5password default tablespace users temporary tablespace temp;  
grant connect,resource to mt5user;  
---  
  
In case backup and Oracle servers are installed on the same computer, connection settings will be as follows:

![oracle_setting_local](images/oracle_setting_local.png)

In case backup and Oracle servers are located on different computers:

![oracle_setting_remote](images/oracle_setting_remote.png)

  * Oracle Database Express Edition has only one database named XE. Therefore, that is the database that should be specified in Data Folder parameter.
  * It is recommended to install Oracle and backup servers on the same computer for faster export. It should also be kept in mind that the backup server itself also consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backups will work close to necessary DBMS.

  
---  
  
Additional export parameters can be selected at [SQL Options (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) tab.

The backup server will immediately start export into the external DBMS after all settings are specified. Request the log of the appropriate backup server using SQL keyword to track the export process: 

2012.10.18 16:33:36 SQL Export Oracle: successfully connected to database 'XE' at 'localhost' as user 'mt5user'  
2012.10.18 16:33:36 SQL Export Oracle: server version Oracle Database 11g Express Edition Release 11.2.0.2.0 - Production  
2012.10.18 16:33:36 SQL Export Oracle: table 'mt5_symbols' creating started  
2012.10.18 16:33:36 SQL Export Oracle: table 'mt5_symbols' created  
2012.10.18 16:33:36 SQL Export Oracle: primary key for 'mt5_symbols' adding started  
2012.10.18 16:33:36 SQL Export Oracle: primary key for 'mt5_symbols' added  
2012.10.18 16:33:36 SQL Export Oracle: table 'mt5_symbols_sessions' creating started  
2012.10.18 16:33:36 SQL Export Oracle: table 'mt5_symbols_sessions' created  
2012.10.18 16:33:36 SQL Export Oracle: primary key for 'mt5_symbols_sessions' adding started  
2012.10.18 16:33:36 SQL Export Oracle: primary key for 'mt5_symbols_sessions' added  
2012.10.18 16:33:36 SQL Export Symbols: 0 symbols and 0 sessions loaded in 203 msecs  
2012.10.18 16:33:36 SQL Export Symbols: synchronization started  
...  
---

```

---

<a id='backup-server-sql-export-installation-and-setup-of-postgresql-md'></a>
### 119. `Backup-Server/SQL-Export/Installation-and-Setup-of-PostgreSQL.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / Installation and Setup of PostgreSQL

[Previous](Installation-and-Setup-of-Oracle.md) | [Next](mt5-symbols.md)

# Installation and Setup of PostgreSQL

Download the required version of PostgreSQL installer from the [official website](https://www.postgresql.org/download/).

> ["Update for Visual C++ 2013 and Visual C++ Redistributable Package"](https://support.microsoft.com/en-us/help/3179560/update-for-visual-c-2013-and-visual-c-redistributable-package) must be installed on the computer where the backup server is installed. Otherwise export to PostgreSQL databases will not be possible.

Run the installation file and follow the on-screen instructions. Choose an installation directory an a set of components:

![Installation of PostgreSQL](images/postgre1.gif)

Next, select the directory, in which the databases will be stored, set a password for the administrator account "postgres". Then specify the port at which the PostgreSQL server will listen to incoming connections.

![Installation of PostgreSQL](images/postgre2.gif)

Next, set the [locale](https://postgrespro.com/docs/postgrespro/9.5/locale.html) to be used by by the database cluster. The locale is inherited from the operating system be default. Locale affects the operation of some SQL requests. In the next steps, click "Next", and wait for the installation to complete.

![Installation of PostgreSQL](images/postgre3.gif)

After installation, run the pgAdmin utility from the Start menu. Connect to the server using the postgres login and the password specified during installation. Next, create a database to export information from MetaTrader 5.

![Creating a database in PostgreSQL](images/postgre_db_create.png)

Then configure data export on the platform site. In case the backup server and PostgreSQL servers are installed on the same computer, connection parameters should be configured as follows:

![Export settings when installing PostgreSQL on the same computer where the backup server is installed](images/postgres_settings_local.png)

In case the backup server and PostgreSQL servers are installed on different computers, connection parameters should be configured as follows:

![Export settings when installing PostgreSQL on a separate computer](images/postgres_settings_remote.png)

  * It is recommended to install PostgreSQL and the backup server on the same computer for faster export. However, it should also be kept in mind that the backup server consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backup servers will run close to necessary DBMS. 


  * All authentication methods are supported for connecting to PostgreSQL, including scram-sha-256.

  
---  
  
Additional export parameters can be selected at [SQL Options (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) tab.

The backup server will immediately start export into the external DBMS after all settings are specified. Request the log of the appropriate backup server using SQL keyword to track the export process:

2017.12.21 15:17:17.154 SQL Export PostgreSQL: server version 10.1   
2017.12.21 15:17:17.156 SQL Export PostgreSQL: successfully connected to database 'metatrader5' at 'localhost' as user 'postgres'   
2017.12.21 15:17:17.170 SQL Export PostgreSQL: table 'mt5_symbols_sessions' creating started   
2017.12.21 15:17:17.180 SQL Export PostgreSQL: table 'mt5_symbols_sessions' created   
...  
---

```

---

<a id='backup-server-sql-export-mt5-accounts-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-accounts.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_accounts

[Previous](mt5-deals/Enumerations.md) | [Next](mt5-prices.md)

# mt5_accounts

Data on the state of trading accounts is exported to the table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Primary key. The login of the client, to whom the trading account belongs.  
CurrencyDigits | Integer | The number of digits after the decimal point in the account deposit currency.  
Balance | Float | The balance of a trade account.  
Credit | Float | The current amount of credit given to an account.  
Margin | Float | The current margin of the account.  
MarginFree | Float | The free margin of an account.  
MarginLevel | Float | The margin level as a percentage. It is calculated as a percentage of the current account equity (Equity) to the margin volume (Margin);  
MarginLeverage | Integer | Margin leverage.  
MarginInitial | Float | The current size of the initial margin of positions on a trading account.  
MarginMaintenance | Float | The current size of the maintenance margin of positions on a trading account.  
Profit | Float | The size of the current profit for all open positions.  
Storage | Float | The current size of swaps charged for open positions on the account.  
Floating | Float | The size of floating profit/loss of open positions on the account. The floating profit/loss is calculated as the sum of Profit, Storage and Commission of open positions on the account.  
Equity | Float | The account equity calculated as a sum of Balance, Credit and Floating.  
BlockedCommission | Float | The amount of the standard commission locked on the account, which has been accumulated during the day/month.  
BlockedProfit | Float | The amount of intraday profit locked on the account.  
Assets | Float | The current total amount of assets on a trading account.  
Liabilities | Float | The current total amount of liabilities on a trading account.

```

---

<a id='backup-server-sql-export-mt5-clients-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-clients.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_clients

[Previous](mt5-managers.md) | [Next](mt5-documents.md)

# mt5_clients

Data about [clients](../../../Platform-Setup/Clients.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
ClientID | Integer | Initial key. Unique entry ID.  
Timestamp | Integer | A unique values within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has changed.  
ClientType | Integer | Client type:

  * 0 — Not specified
  * 1 — Individual
  * 2 — Corporate
  * 3 — Fund

  
ClientStatus | Integer | Client status:

  * 0 — Not registered
  * 1 — Registered
  * 2 — not interested
  * 3 — Not completed
  * 4 — Completed
  * 5 — Information
  * 6 — Rejected
  * 7 — Approved
  * 8 — Financed
  * 9 — Active
  * 10 — Inactive
  * 11 — Suspended
  * 12 — Closed
  * 13 — Deleted

  
AssignedManager | Integer | The login of the assigned manager.  
DateCreated | Integer | Client creation date.  
DateModified | Integer | Client's last modification date.  
Comment | String | A comment to the client.  
ComplianceApprovedBy | Integer | The login of the manager by whom the client was approved.  
ComplianceClientCategory | String | Client compliance category. Currently not used.  
ComplianceDateApproval | DateTime | The date when the client was approved, in the format of YYYY-MM-DD HH:MM:SS  
ComplianceDateTermination | DateTime | The date when the provision of services to the client was discontinued, in the format of YYYY-MM-DD HH:MM:SS  
LeadCampaign | String | The website from which the client came (lead source).  
LeadSource | String | The name of the marketing campaign, as a result of which the client came (lead campaign).  
Introducer | String | The login of the user by whom the client was introduced.  
PersonTitle | String | Client's title.  
PersonName | String | First name and last name  
PersonMiddleName | String | Middle name.  
PersonBirthDate | DateTime | Date of birth, in the format of YYYY-MM-DD HH:MM:SS  
PersonCitizenship | String | Citizenship.  
PersonGender | Integer | Gender:

  * 0 — Not specified
  * 1 — male
  * 2 — Female

  
PersonTaxID | String | Client's Tax ID.  
PersonDocumentType | String | Document type of document: passport, driver's license, etc.  
PersonDocumentNumber | String | Document number.  
PersonDocumentDate | DateTime | Document issue date, in the format of YYYY-MM-DD HH:MM:SS  
PersonDocumentExtra | String | Additional document information.  
PersonEmployment | Integer | Employment status:

  * 0 — Unemployed
  * 1 — Employed
  * 2 — Entrepreneur or self-employed
  * 3 — Retired
  * 4 — Student
  * 5 — Other

  
PersonIndustry | Integer | Employment area:

  * 0 — Not specified
  * 1 — Agriculture, Food and Natural Resources
  * 2 — Architecture and Construction
  * 3 — Business Administration and Management
  * 4 — Art, Audio/Video Technology and Communication
  * 5 — Education and Training
  * 6 — State and Administrative Management
  * 7 — Health
  * 8 — Tourism and Hospitality
  * 9 — Information Technology
  * 10 — Legal and Public Safety, Correction and Protection Services
  * 11 — Manufacturing
  * 12 — Marketing and Sales
  * 13 — Science and Technology
  * 14 — Engineering and Mathematics
  * 15 — Transportation, Distribution and Logistics
  * 16 — other

  
PersonEducation | Integer | Education:

  * 0 — Not specified
  * 1 — Secondary
  * 2 — Bachelor's degree or equivalent
  * 3 — Master's degree or equivalent
  * 4 — PhD or equivalent
  * 5 — other

  
PersonWealthSource | Integer | Source of income:

  * 0 — Employment/business activity
  * 1 — Savings or investments
  * 2 — Gift or inheritance
  * 3 — other

  
PersonAnnualIncome | Float | Annual income.  
PersonNetWorth | Float | Net assets.  
PersonAnnualDeposit | Float | Annual deposit.  
CompanyName | String | Company name.  
CompanyRegNumber | String | Company registration number.  
CompanyRegDate | String | company registration date.  
CompanyRegAuthority | String | Company registration authority.  
CompanyVat | String | VAT number.  
CompanyLei | String | LEI number for EMIR reports.  
CompanyLicenseNumber | String | Company license number.  
CompanyLicenseAuthority | String | Licensing authority.  
CompanyCountry | String | Country of incorporation.  
CompanyAddress | String | Company's legal address.  
CompanyWebsite | String | Company's webiste.  
ContactPreferred | Integer | Preferred method of communication:

  * 0 — Not specified
  * 1 — Email
  * 2 — Telephone
  * 3 — SMS
  * 4 — Messenger

  
ContactLanguage | String | Client's language.  
ContactEmail | String | Client's email.  
ContactPhone | String | Phone number.  
ContactMessengers | String | Messengers.  
ContactSocialNetworks | String | Accounts in social networks.  
ContactLastDate | DateTime | Last contact date, in the format of YYYY-MM-DD HH:MM:SS  
AddressCountry | String | Client's country.  
AddressPostcode | String | Client's postal code.  
AddressStreet | String | Client's address.  
AddressState | String | State/region of residence.  
AddressCity | String | City.  
ExperienceFX | Integer | Forex trading experience, number of years.  
ExperienceCFD | Integer | CFD trading experience, number of years.  
ExperienceFutures | Integer | Futures trading experience, number of years.  
ExperienceStocks | Integer | Stock trading experience, number of years.  
ClientOrigin | Integer | How the client record was created:

  * 0 — manually
  * 1 — based on a demo account
  * 2 — based on a contest account
  * 3 — based on a preliminary account
  * 4 — based on a real account

  
ClientOriginLogin | Integer | The number of the account, based on which the client record was created.

```

---

<a id='backup-server-sql-export-mt5-commissions-tiers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-commissions-tiers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_commissions_tiers

[Previous](mt5-commissions.md) | [Next](mt5-managers.md)

# mt5_commissions_tiers

[Commission levels (#level)](../../../Platform-Setup/Groups/Commission-Settings.md#level) are exported to this table. The table contains the following fields:

Name | Type | Purpose  
Tier_ID | Integer | Initial key. Unique [commission level ID (#level)](../../../Platform-Setup/Groups/Commission-Settings.md#level).  
Commission_ID | Integer | [ID of the commission setting (#commissions)](../../../Platform-Setup/Groups/Group-Settings.md#commissions) the level belongs to.  
Mode | Integer | Commission calculation unit:

  * 0 — account currency
  * 1 — base currency
  * 2 — profit currency
  * 3 — margin currency
  * 4 — points
  * 5 — percentage
  * 6 — specified currency

  
Type | Integer | Commission charge type:

  * 0 — per trade
  * 1 — per volume

  
Value | Float | Commission sum. Commission units depend on the commission calculation method (Mode).  
RangeFrom | Float | The minimum deal volume (turnover), from which the commission will be charged.  
RangeTo | Float | The maximum trade volume (turnover), from which the commission will be charged.  
Minimal | Float | The minimum amount of commission. The value is specified in the group deposit currency.  
Currency | String | Commission calculation currency (if "Specified currency" is selected in the Mode field).

```

---

<a id='backup-server-sql-export-mt5-commissions-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-commissions.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_commissions

[Previous](mt5-groups-symbols.md) | [Next](mt5-commissions-tiers.md)

# mt5_commissions

[Commission settings for groups](../../../Platform-Setup/Groups/Commission-Settings.md) are exported to this table. The table contains the following fields:

Name | Type | Purpose  
Commission_ID | Integer | Initial key. A unique [commission setting ID (#commissions)](../../../Platform-Setup/Groups/Group-Settings.md#commissions).  
Group_ID | Integer | [ID of the group](mt5-groups.md), a commission setting belongs to.  
Name | String | Commission setting name (up to 64 characters).  
Description | String | Commission setting description (up to 64 characters).  
Path | String | Path to a symbol or a group of symbols covered by a commission setting.  
Mode | Integer | Commission type: 0 — standard, 1 — agent.  
ModeRange | Integer | Commission [levels type (#level)](../../../Platform-Setup/Groups/Commission-Settings.md#level):

  * 0 — volume
  * 1 — turnover in money
  * 2 — turnover in volume

  
ModeCharge | Integer | Commission [charge mode (#charge)](../../../Platform-Setup/Groups/Commission-Settings.md#charge):

  * 0 — daily
  * 1 — monthly
  * 2 — instant

  
TurnoverCurrency | String | Currency, in which the [money turnover (#level)](../../../Platform-Setup/Groups/Commission-Settings.md#level) is calculated.  
ModeEntry | Integer | Commission calculation mode depending on the trade direction:

  * 0 — all trades regardless of direction.
  * 1 — only entry deals.
  * 2 — only exit deals.

  
ModeAction | Integer | Commission calculation mode depending on the trade type:

  * 0 — all trades regardless of type.
  * 1 — only Buy deals.
  * 2 — only Sell deals.

  
ModeProfit | Integer | Commission calculation modes depending on the deal profit:

  * 0 — all deals.
  * 1 — only profitable deals.
  * 2 — only losing deals.

  
ModeReason | Integer | Commission calculation modes depending on the reason for the deal.

  * 0x00000000 — no commission will be charged for any trades.
  * 0x00000001 — the deal was performed by the client manually via the client terminal.
  * 0x00000002 — the deal was performed by the client using an Expert Advisor.
  * 0x00000004 — the deal was performed by a dealer via the Manager terminal.
  * 0x00000008 — the deal was performed from an external trading system.
  * 0x00000010 — the deal was performed via the MetaTrader 5 mobile terminal for Android or iPhone.
  * 0x00000020 — the deal was performed via the web terminal.
  * 0x00000040 — the deal was performed as a result of copying of a trading signal, in accordance with the subscription, in the client terminal.



```

---

<a id='backup-server-sql-export-mt5-daily-orders-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-daily-orders.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_daily_orders

[Previous](mt5-daily.md) | [Next](mt5-daily-positions.md)

# mt5_daily_orders

Data on the end-of-day status of open [orders](../../../Platform-Setup/Orders.md) is exported to this table. The table is generated only if the [backup server settings (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) have the "Export additional columns for daily reports \ Orders from daily reports" option enabled. The table contains the following fields:

Name | Type | Description  
Datetime | DateTime | The date for which the order status was saved.  
Order | Integer | Primary key. Order ticket.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
ExternalID | String | The order ID in external trading systems.  
Login | Integer | The login of the client, to whom the order belongs.  
Dealer | Integer | The login of a dealer, who has processed an order.  
Symbol | String | The symbol of an order.  
Digits | Integer | The number of decimal places in the price of an order.  
DigitsCurrency | Integer | The number of decimal places the deposit currency of the client who has placed the order.  
ContractSize | Float  | The contract size of the symbol, for which an order was placed.  
State | Integer | The current state of an order. Passed as a value of the [EnOrderMode (#enorderstate)](mt5-orders/Enumerations.md#enorderstate) enumeration.  
Reason | Integer | The reason for placing the order. Passed as a value of the [EnOrderReason (#enorderreason)](mt5-orders/Enumerations.md#enorderreason) enumeration.  
TimeSetup | DateTime | Order placement time in the YYYY-MM-DD HH:MM:SS format.  
TimeSetupMsc | DateTime | Order placement time in milliseconds in the YYYY-MM-DD HH:MM:SS.MS format.  
TimeExpiration | DateTime | Order expiration time in the YYYY-MM-DD HH:MM:SS format.  
TimeDone | DateTime | Order execution time in the YYYY-MM-DD HH:MM:SS format.  
TimeDoneMsc | DateTime | Order execution time in milliseconds in the YYYY-MM-DD HH:MM:SS.MS format.  
ModifyFlags | Integer | The order modification flags. Passed as a value of the [EnTradeModifyFlags (#entrademodifyflags)](mt5-orders/Enumerations.md#entrademodifyflags) enumeration (sum of values of appropriate flags).  
Type | Integer | Order type. Passed as a value of the [EnOrderType (#enordertype)](mt5-orders/Enumerations.md#enordertype) enumeration.  
TypeFill | Integer | Order filling type. Passed as a value of the [EnOrderFilling (#enorderfilling)](mt5-orders/Enumerations.md#enorderfilling) enumeration.  
TypeTime | Integer | Order expiration type. Passed in a value of the [EnOrderTime (#enordertime)](mt5-orders/Enumerations.md#enordertime) enumeration.  
PriceOrder | Float  | Order price.  
PriceTrigger | Float | The order triggering price.  
PriceCurrent | Float | The current price of the symbol, for which an order has been placed.  
PriceSL | Float | The Stop Loss level of an order.  
PriceTP | Float | The Take Profit level of an order.  
VolumeInitial | Integer | The initial order volume. One unit corresponds to 1/10000 lot.  
VolumeInitialExt | Integer | The initial order volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeCurrent | Integer | The current unfilled volume of an order. One unit corresponds to 1/10000 lot.  
VolumeCurrentExt | Integer | The current unfilled order volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
ExpertID | Integer | The ID of the Expert Advisor that has placed the order.  
PositionID | Integer | The position ID (ticket) set in the order.  
PositionByID | Integer | The opposite position ID (ticket) set in the order. The property is set for Close By operations ([OP_CLOSE_BY (#enordertype)](mt5-orders/Enumerations.md#enordertype)). The ticket of the position that is closed by the opposite one is set in PositionID.  
Comment | String | A comment to an order.  
ActivationMode | Integer | Order activation type. Passed in a value of the [EnOrderActivation (#enorderactivation)](mt5-orders/Enumerations.md#enorderactivation) enumeration.  
ActivationTime | DateTime | Order activation time in the YYYY-MM-DD HH:MM:SS format.  
ActivationPrice | Float | The price, at which the order was activated.  
ActivationFlags | Integer | Order activation flags. Passed as a value of the [EnTradeActivationFlags (#entradeactivationflags)](mt5-orders/Enumerations.md#entradeactivationflags) enumeration (sum of values of appropriate flags).  
RateMargin | Float | The rate of conversion of the margin currency of the symbol to the deposit currency of the user, which is used when calculating the margin requirements for the order.  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{pos:0,app_id:1,valInt:500,valUInt:500,valDbl:0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.

```

---

<a id='backup-server-sql-export-mt5-daily-positions-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-daily-positions.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_daily_positions

[Previous](mt5-daily-orders.md) | [Next](mt5-holidays.md)

# mt5_daily_positions

Data on the end-of-day status of positions is exported to this table. The table is generated only if the [backup server settings (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) have the "Export additional columns for daily reports \ Orders from daily reports" option enabled. The table contains the following fields:

Name | Type | Description  
Datetime | DateTime | The date for which the position status was saved.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Login | Integer | The login of the client, to whom the trade position belongs.  
Symbol | String | The symbol of a trade position.  
Action | Integer | Position type. Passed in a value of the [EnPositionAction (#enpositionaction)](mt5-positions/Enumerations.md#enpositionaction) enumeration.  
Digits | Integer | The number of decimal places in the price of a position.  
DigitsCurrency | Integer | The number of decimal places the deposit currency of the client who has opened the position.  
Reason | Integer | The reason for position opening. Passed in a value of the [EnPositionReason (#enpositionreason)](mt5-positions/Enumerations.md#enpositionreason) enumeration.  
ContractSize | Float | The contract size of the symbol, for which a position is opened.  
Position | Integer | The ticket (unique identifier) of a trade position in a MetaTrader 5 platform.  
ExternalID | String | The position ticket (unique number) in an external trading system.  
TimeCreate | DateTime | Time of position creation, in seconds that have elapsed since 01.01.1970.  
TimeUpdate | DateTime | Time of the last modification of a position, in seconds that have elapsed since 01.01.1970. The modification time of a position is the time of the last modification of its volume. Virtually, it is the time of the last deal performed by the financial instrument that corresponds to that position.  
TimeCreateMsc | DateTime | Position generation time in the YYYY-MM-DD HH:MM:SS.MS format.  
TimeUpdateMsc | DateTime | Time of a trading position last change in the YYYY-MM-DD HH:MM:SS.MS format. The modification time of a position is the time of the last modification of its volume. Virtually, it is the time of the last deal performed by the financial instrument that corresponds to that position.  
PriceOpen | Float | The weighted average open price of a position. Calculated by the following formula: (price of deal 1 * volume of deal 1 1 + ... + price of deal N * volume of deal N) / (volume of deal 1 + ... + volume of deal N).  
PriceCurrent | Float | The current price of the symbol, for which a trade position has been opened.  
PriceSL | Float | The Stop Loss level of a trade position.  
PriceTP | Float | The Take Profit level of a trade position.  
Volume | Integer | The volume of a trade position. One unit corresponds to 1/10000 lot.  
VolumeExt | Integer | The trade position volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
Profit | Float | Returns of a trade position in deposit currency.  
Storage | Float | The swap size for a position in deposit currency.  
RateProfit | Float | The exchange rate of the profit currency of a position to the deposit currency of a client group.  
RateMargin | Float | The exchange rate of the margin currency of a position to the client's deposit currency.  
ExpertID | Integer | The ID of the Expert Advisor that has opened the position.  
ExpertPositionID | Integer | Position ID.  
Comment | String | A comment to a position.  
Dealer | Integer | The login of a dealer, who has processed an order, which opened the position.  
ActivationMode | Integer | Position activation type. Passed in a value of the [EnActivation (#enactivation)](mt5-positions/Enumerations.md#enactivation) enumeration.  
ActivationTime | DateTime | Position activation time in the YYYY-MM-DD HH:MM:SS.MS format.  
ActivationPrice | Float | Position activation price.  
ActivationFlags | Integer | Position activation flags. Passed as a value of the [EnTradeActivationFlags (#entradeactivationflags)](mt5-positions/Enumerations.md#entradeactivationflags) enumeration (sum of values of appropriate flags).  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{pos:0,app_id:1,valInt:500,valUInt:500,valDbl:0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.

```

---

<a id='backup-server-sql-export-mt5-daily-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-daily.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_daily

[Previous](mt5-prices.md) | [Next](mt5-daily-orders.md)

# mt5_daily

Daily reports generated for clients are exported to the table. The table contains the following fields:

Name | Type | Description  
Datetime | DateTime | The date and time of the daily report generation.  
Login | Integer | The login of the client for whom the daily report is generated.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
DatetimePrev | DateTime | Date and time of the previous daily report generation in the YYYY-MM-DD HH:MM:SS.  
Name | String | The name of a client in the daily report  
Group | String | The group of a client in a daily report.  
Currency | String | The client's deposit currency in a daily report.  
Company | String | The company serving the client in a daily report.  
EMail | String | An email of a client in a daily report.  
Balance | Float | The size of a client's balance in a daily report.  
Credit | Float | The amount of a client's credit funds in a daily report.  
InterestRate | Float | The amount of accumulated annual interest. Annual interest is calculated every day in accordance with the [group settings (#interest)](../../../Platform-Setup/Groups/Group-Settings.md#interest) and is accumulated in a separate account field. At the end of each month, the accumulated amount is credited to the account balance using an [Interest rate (#action)](../../../Platform-Setup/Deals.md#action) operation, and the InterestRate value is reset to zero.  
CommissionDaily | Float | The amount of a client's commissions for a day in a report.  
CommissionMonthly | Float | The total amount of a client's commissions for the current month in a report.  
AgentDaily | Float | The amount of agent commission charged for a client's trade operations for a reported day.  
AgentMonthly | Float | The amount of agent commission charged for a client's trade operations for the current month.  
BalancePrevDay | Float | The value of a client's balance as of the end of the previous day.  
BalancePrevMonth | Float | The value of a client's balance as of the end of the current month.  
EquityPrevDay | Float | The value of a client's equity as of the end of the previous day.  
EquityPrevMonth | Float | The value of a client's equity as of the end of the previous trading month.  
Margin | Float | The size of a client's margin in a daily report.  
MarginFree | Float | A client's free margin in a daily report.  
MarginLevel | Float | The margin level of a client in a daily report.  
MarginLeverage | Integer | The margin leverage of a client in a daily report.  
Profit | Float | The size of the current profit for all open positions of a client in a daily report.  
ProfitStorage | Float | The current size of swaps charged for a client's open positions for a day, but not yet reflected in the balance.  
ProfitEquity | Float | The amount of the current floating equity of a client in a daily report.  
ProfitAssets | Float | The current amount of a client's assets in a daily report. It is only used for the [Exchange risk management model (#risk)](../../../Platform-Setup/Groups/Group-Settings.md#risk).  
ProfitLiabilities | Float | The current amount of a client's liabilities in a daily report. It is only used for the [Exchange risk management model (#risk)](../../../Platform-Setup/Groups/Group-Settings.md#risk).  
DailyProfit | Float | The amount of a client's daily profit.  
DailyBalance | Float | The amount accrued to a client's balance during the reported day.  
DailyCredit | Float | The amount of credit given to a client during the reported day.  
DailyCharge | Float | The amount of other charges to the client's balance during the reported day.  
DailyCorrection | Float | The amount of corrective balance operations for a reported day.  
DailyBonus | Float | The amount of bonuses added to the client's balance for the reported day.  
DailyStorage | Float | The amount of swaps calculated for the client for a reported day.  
DailyCommInstant | Float | The amount of instant commissions charged from the client for a reported day.  
DailyCommRound | Float | The amount of turnover commissions charged from the client for a reported day.  
DailyCommFee | Float | The [fee](../../../Platform-Setup/Groups/Commission-Settings.md) amount charged for the client's deals for the reported day.  
DailyDividend | Float | The amount of dividends accrued to the client for a reported day.  
DailyTaxes | Float | The amount of taxes withheld from the client for the reported day.  
DailySOCompensation | Float | The amount of negative balance compensation accrued to the client for a reported day.  
DailyAgent | Float | The amount of agent commission charged for a client's trade operations for a reported day.  
DailyInterest | Float | The amount accrued to a client as part of the annual interest rate for the reported day.

```

---

<a id='backup-server-sql-export-mt5-deals-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-deals.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_deals

[Previous](mt5-positions/Enumerations.md) | [Next](mt5-deals/Enumerations.md)

# mt5_deals

Data on [deals](../../../Platform-Setup/Deals.md) is exported to the table. If ["Export history orders and deals into separate tables by years" (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) option is enabled in settings, deals for each year are exported to a separate table. A year is specified in the table heading, for example, mt5_deals_2012. If the option is disabled, all deals are exported to a single mt5_deals table.

The table contains the following fields:

Name | Type | Description  
Deal | Integer | Primary key. The ticket of a deal.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Login | Integer | The login of the client, to whom the deal belongs.  
Dealer | Integer | The login of a dealer, who has processed a deal.  
Order | Integer | The ticket of the order, as a result of which a deal was executed.  
Action | Integer | Type of action performed with a deal. Passed in a value of the [EnDealAction (#endealaction)](mt5-deals/Enumerations.md#endealaction) enumeration.  
Entry | Integer | Deal direction. Passed in a value of the [EnEntryFlags (#enentryflags)](mt5-deals/Enumerations.md#enentryflags) enumeration.  
Digits | Integer | The number of decimal places in the price of a deal.  
DigitsCurrency | Integer | The number of decimal places the deposit currency of the client who has executed the deal.  
ContractSize | Float | The contract size of the symbol, for which a deal was executed.  
Time | DateTime | Trade execution time in the YYYY-MM-DD HH:MM:SS format.  
Symbol | String | The symbol, for which a deal is executed.  
Price | Float | The price of the deal.  
PriceSL | Float | The Stop Loss level of a deal. Stop Loss values for entry and reversal deals are set in accordance with the Stop Loss of orders, which initiated these deals. The Stop Loss values ​​of appropriate positions as of the time of position closing are used for exit deals.  
PriceTP | Float | Take Profit values for entry and reversal deals are set in accordance with the Take Profit of orders, which initiated these deals. The Take Profit values ​​of appropriate positions as of the time of position closing are used for exit deals.   
Volume | Integer | The deal volume. One unit corresponds to 1/10000 lot.  
VolumeExt | Integer | The deal volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeClosed | Integer | The position volume that was closed by the deal. One unit corresponds to 1/10000 lot.  
VolumeClosedExt | Integer | The extended accuracy volume of a position that was closed by this deal. One unit corresponds to 1/100000000 lot.  
Profit | Float | Profit from a deal.  
Value | Float | The deal value in client deposit currency.  
Storage | Float | The swap size for a deal.  
Commission | Float | The amount of [commission](../../../Platform-Setup/Groups/Commission-Settings.md) charged for a deal.  
Fee | Float | [Fee](../../../Platform-Setup/Groups/Commission-Settings.md) per deal.  
RateProfit | Float | The exchange rate of the profit currency of a deal to the deposit currency of a client group.  
RateMargin | Float | The exchange rate of the margin currency of a deal to the client's deposit currency.  
ExpertID | Integer | The ID of the Expert Advisor that has executed a deal.  
PositionID | Integer | The position identifier (ticket) for a deal.  
Comment | String | Comment to a deal.  
ProfitRaw | Float | The amount of return resulting from a deal. Return is specified in the profit currency of the symbol, for which the deal is executed.  
PricePosition | Float | The price of the position closed with this deal.  
TickValue | Float | The tick value price for a deal.  
TickSize | Float | The tick size for a deal.  
Flags | Integer | The common flags of a deal. This parameter is reserved for future use.  
Reason | Integer | The reason for performing a deal. Passed in a value of the [EnDealReason (#endealreason)](mt5-deals/Enumerations.md#endealreason) enumeration.  
Gateway | String | The ID of a gateway, using which a deal was performed.  
PriceGateway | Float | The price that was actually used for performing a deal through a gateway in an external trading system without taking in consideration its price transformation settings of the gateway.  
MarketBid | Float | The market Bid price as at the time of deal execution by the server. The field is only filled for the deals which were created after the platform was updated to build 2890 or higher. For earlier deals, the value will be zero.  
MarketAsk | Float | The market Ask price as at the time of deal execution by the server. The field is only filled for the deals which were created after the platform was updated to build 2890 or higher. For earlier deals, the value will be zero.  
MarketLast | Float | The market Last price as at the time of deal execution by the server. The field is only filled for the deals which were created after the platform was updated to build 2890 or higher. For earlier deals, the value will be zero.  
TimeMsc | DateTime | Trade execution time in the YYYY-MM-DD HH:MM:SS.MS format.  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{"pos":0,"app_id":1,"valInt":500,"valUInt":500,"valDbl":0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.

```

---

<a id='backup-server-sql-export-mt5-documents-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-documents.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_documents

[Previous](mt5-clients.md) | [Next](mt5-users.md)

# mt5_documents

Data about [client documents (#documents)](../../../Platform-Setup/Clients.md#documents) is exported to this table. The table contains the following fields:

Name | Type | Description  
DocumentID | Integer | Initial key. Unique document ID.  
Timestamp | Integer | A unique values within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has changed.  
RelatedClient | Integer | The ID of the client to whom the document belongs. Corresponds to Client ID from the [mt5_clients](mt5-clients.md) table.  
ApprovedDate | DateTime | Document approval date, in the format of YYYY-MM-DD HH:MM:SS  
ApprovedBy | Integer | The login of the manager by whom the document was approved.  
DateIssue | DateTime | Document issue date, in the format of YYYY-MM-DD HH:MM:SS  
DateExpiration | DateTime | Document expiration date, in the format of YYYY-MM-DD HH:MM:SS  
DocumentType | Integer | Document type:

  * 0 — Other
  * 1 — Proof of identity
  * 2 — Proof of address
  * 3 — Registration address
  * 4 — CEO's ID document
  * 5 — Certificate of Registration
  * 6 — Certificate of Directors
  * 7 — Certificate of good standing

  
DocumentName | String | Document name.  
DocumentComment | String | Comment to the document.  
DocumentStatus | Integer | Document status:

  * 0 — New
  * 1 — Approved
  * 2 — Rejected
  * 3 — Archived
  * 4 — Deleted

  
  
> Only document data is exported to SQL. Document files themselves are not exported.

```

---

<a id='backup-server-sql-export-mt5-feeder-params-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-feeder-params.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_feeder_params

[Previous](mt5-feeder-translates.md) | [Next](mt5-feeder-symbols.md)

# mt5_feeder_params

Data about [additional settings of data feeds (#parameters)](../../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) is exported to this table. The table contains the following fields:

Name | Type | Description  
ParamID | String | The unique identifier of the parameter.  
Feeder | String | The name of the data feed, to which the setting applies.  
Type | Integer | Parameter type:

  * 0 — string
  * 1 — integer
  * 2 — floating-point number
  * 3 — time
  * 4 — date
  * 5 — date and time
  * 6 — list of groups
  * 7 — list of symbols

  
Name | String | The name of the parameter.  
Value | String | The value of the parameter.

```

---

<a id='backup-server-sql-export-mt5-feeder-symbols-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-feeder-symbols.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_feeder_symbols

[Previous](mt5-feeder-params.md) | [Next](mt5-reports.md)

# mt5_feeder_symbols

Data on [symbol settings for data feeds (#symbols)](../../../Platform-Setup/Data-Feeds/Configuration-of.md#symbols) is exported to this table. The table contains the following fields:

Issued to | Type | Description  
Symbol_ID | Integer | Unique entry ID.  
FeederName | String | The name of the data feed, to which the configuration applies.  
Symbol | String | The name of the symbol in the trading platform.

```

---

<a id='backup-server-sql-export-mt5-feeder-translates-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-feeder-translates.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_feeder_translates

[Previous](mt5-feeders/Enumerations.md) | [Next](mt5-feeder-params.md)

# mt5_feeder_translates

Data about [conversion settings of data feeds (#translation)](../../../Platform-Setup/Data-Feeds/Configuration-of.md#translation) is exported to this table. The table contains the following fields:

Name | Type | Description  
Symbol | String | The name of the symbol in the trading platform.  
Feeder | String | The name of the data feed, to which the conversion setting applies.  
Source | String | The name of the symbol on the source server.  
BidMarkup | Integer | Markup for the symbol's Bid price received from the data feed.  
AskMarkup | Integer | Markup for the symbol's Ask price received from the data feed.  
Digits | Integer | The number of digits after the decimal point in the price of the symbol that receives quotes.

```

---

<a id='backup-server-sql-export-mt5-feeders-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-feeders.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_feeders

[Previous](mt5-routing-conds.md) | [Next](mt5-feeders/Enumerations.md)

# mt5_feeders

Data about [data feed settings](../../../Platform-Setup/Data-Feeds.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Name | String | Get and set the data feed name.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Module | String | The name of the data feed module.  
GatewayServer | String | The addresses at which the data feed will accept connections from the history server.  
FeedServer | String | The addresses of the server to which the data feed is connected.  
Enable | Integer | The data feed configuration status: 0 — disabled, 1 — enabled.  
Mode | Integer | Data feed operation mode. Passed using the [EnFeedersMode (#enfeederflags)](mt5-feeders/Enumerations.md#enfeederflags) enumeration as a sum of flags. For example, 1 means that the data feed receives news, 9 — receives news while working in the "remote datafeed" mode.  
Timeout | Integer | Timeout of a data feed before reconnecting.  
TimeoutReconnect | Integer | Timeout between attempts to reconnect to the source server.  
TimeoutSleep | Integer | Timeout between the series of reconnections to the source server.  
AttemptsSleep | Integer | The number of attempts in the series of reconnections to the source server.  
Symbols | String | The list of symbols for which the data feed provides quotes.  
SysConnection | Integer | The status of the data feed connection to a source server. 0 — no connection, 1 — connected.  
SysLastTime | DateTime | The time of the last reconnection to the source server in the YYYY-MM-DD HH:MM:SS.MSC format.  
Company | String | The name of the company who signed the executable file of the data feed.  
Issuer | String | The certification authority that issued the certificate of the above company.  
TickStatsCount | Integer | The amount of price statistics received by the data feed from an external data source during the current session.  
TicksCount | Integer | The number of price changes received by the data feed from an external data source during the current session.  
BooksCount | Integer | The number of Market Depth changes received by the data feed from an external data source during the current session.  
NewsCounts | Integer | The number of news items received by the data feed from an external data source during the current session.  
BytesReceived | Integer | The volume of traffic (in bytes) received by the data feed during the current session.  
BytesSent | Integer | The volume of traffic (in bytes) sent by the data feed during the current session.  
StateFlags | Integer | Flags of states.

```

---

<a id='backup-server-sql-export-mt5-firewall-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-firewall.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_firewall

[Previous](mt5-network-backup-folders.md) | [Next](mt5-routing.md)

# mt5_firewall

Data on the [firewall settings](../../../Platform-Setup/Security/Firewall.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Action | Integer | The type of actions undertaken in accordance with the firewall rule:

  * 0 — block
  * 1 — allow
  * 2 — always allow

  
From | String | Beginning of the range of the IP addresses the firewall rule is applied to.  
To | String | End of the range of the IP addresses the firewall rule is applied to.  
Comment | String | A comment to the firewall rule.

```

---

<a id='backup-server-sql-export-mt5-gateways-params-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-gateways-params.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_gateways_params

[Previous](mt5-gateways.md) | [Next](mt5-gateways-translates.md)

# mt5_gateways_params

Data about [additional report settings (#parameters)](../../../Platform-Setup/Gateways/Configuration-of.md#parameters) is exported to this table. The table contains the following fields:

Name | Type | Description  
ParamID | String | The unique identifier of the parameter.  
GatewayName | String | The name of the gateway configuration the setting applies to.  
Type | Integer | Parameter type:

  * 0 — string
  * 1 — integer
  * 2 — floating-point number
  * 3 — time
  * 4 — date
  * 5 — date and time
  * 6 — list of groups
  * 7 — list of symbols

  
Name | String | Parameter name.  
Value | String | Parameter value.

```

---

<a id='backup-server-sql-export-mt5-gateways-symbols-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-gateways-symbols.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_gateways_symbols

[Previous](mt5-gateways-translates.md) | [Next](../../Data-Feeds.md)

# mt5_gateways_symbols

Data on [symbol settings for gateways (#symbols)](../../../Platform-Setup/Gateways/Configuration-of.md#symbols) is exported to this table. The table contains the following fields:

Issued to | Type | Description  
Symbol_ID | Integer | Unique entry ID.  
GatewayName | String | The name of the data feed, to which the configuration applies.  
Symbol | String | The name of the symbol in the trading platform.

```

---

<a id='backup-server-sql-export-mt5-gateways-translates-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-gateways-translates.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_gateways_translates

[Previous](mt5-gateways-params.md) | [Next](mt5-gateways-symbols.md)

# mt5_gateways_translates

Data about [price translation settings in the gateway (#translation)](../../../Platform-Setup/Gateways/Configuration-of.md#translation) is exported to this table. The table contains the following fields:

Name | Type | Description  
Symbol | String | The name of the symbol in the trading platform.  
GatewayName | String | The name of the gateway configuration the setting applies to.  
Server | Integer | The ID of the trade server, for which the plugin is configured.  
Source | String | The symbol name in the data feed, to which the gateway connects.  
BidMarkup | Integer | Correction for the Bid price received for a symbol from the data source, to which the gateway connects.  
AskMarkup | Integer | Correction for the Ask price received for a symbol from the data source, to which the gateway connects.  
Digits | Integer | The number of digits after the decimal point in the price of the symbol that receives quotes.

```

---

<a id='backup-server-sql-export-mt5-gateways-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-gateways.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_gateways

[Previous](mt5-time-weekdays.md) | [Next](mt5-gateways-params.md)

# mt5_gateways

Data on the [gateway settings](../../../Platform-Setup/Gateways.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Name | String | Gateway configuration name.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Module | String | Gateway module name.  
GatewayServer |  | The address at which the gateway accepts connections from the history and trade servers.  
TradingServer |  | Address of the server to which the gateway connects.  
Enable | Integer | Gateway operation mode: 0 — disabled, 1 — enabled.  
Flags | Integer | Gateway operation flags:

  * 0x00000001 — gateway works as a remote application.
  * 0x00000002 — gateway is allowed to import symbol settings.
  * 0x00000004 — do not broadcast quotes from the gateway in the system.
  * 0x00000008 — gateway can manage clients' balances using IMTExecution::TE_BALANCE_CHANGE and IMTExecution::TE_BALANCE_CORRECT trade executions.
  * 0x00000010 — if enabled, the gateway log receives additional operation data, including the results of measuring the trading operations handling speed. A more detailed information on extended logging is provided in the [Journal of Gateways](../../../Platform-Setup/Gateways/Journal-of.md) section.
  * 0x00000020 — gateway supports requesting the state of external trading system positions. The request is made from the [Positions](../../../Platform-Setup/Gateways/Positions.md) tab of the gateway. 
  * 0x00000040 — collect advanced metrics related to request processing by the gateway.
  * 0x00000100 — gateway is running in demo mode. The mode is checked based on the license at the time the module is loaded.
  * 0x00000200 — gateway is integrated into the platform.

  
Gateway | String | Gateway module name.  
TimeoutReconnect | Integer | Timeout between attempts to reconnect to an external server in seconds.  
TimeoutSleep | Integer | Timeout between the series of reconnections to an external server in seconds.  
AttempsSleep | Integer | Number of attempts in a series of reconnections to an external server.  
ID | Integer | The gateway ID.  
Symbols | Array | The list of symbols for which the gateway provides quotes and processes trading operations.  
SysConnection | Integer | The state of gateway connection to an external trading system: 0 — connected, 1 — disconnected.  
SysLastTime | Integer | The time of the last successful gateway connection to an external trading system in the YYYY-MM-DD HH:MM:SS.MS format.  
Company | String | The company by which the gateway executable is signed.  
Issuer | String | The certification authority that issued the certificate to the above company.  
TickStatsCount | Integer | The number of price statistics changes received by the gateway from the external system for the current session.  
TicksCount | Integer | The number of price changes received by the gateway from the external system for the current session.  
BooksCount | Integer | The number of Market Depth changes received by the gateway from an external trading system for the current session.  
TradeAverageTime | Integer | Average time spent by the gateway to process one trading operation in milliseconds.  
TradeRequestsCount | Integer | The number of trading operations processed by the gateway during the current session.  
BytesReceived | Integer | Traffic volume received by the gateway during the current session.  
BytesSent | Integer | Traffic volume sent by the gateway during the current session.  
StateFlags | Integer | Flags of states. Currently not used.

```

---

<a id='backup-server-sql-export-mt5-groups-symbols-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-groups-symbols.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_groups_symbols

[Previous](mt5-groups/Enumerations.md) | [Next](mt5-commissions.md)

# mt5_groups_symbols

Individual [symbol settings for groups](../../../Platform-Setup/Groups/Group-Symbol-Settings.md) are exported to the table. The table contains the following fields:

Name | Type | Description  
Symbol_ID | Integer | Primary key. Unique symbol ID for the group.  
Group_ID | Integer | [ID of the group](mt5-groups.md), to which symbol settings are applied.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Path | String | The path to a symbol or group of symbols that are subject to the special group settings.  
TradeMode | Integer | The symbol trading mode for the group. Passed in a value of the [EnTradeMode (#entrademode)](mt5-symbols/Enumerations.md#entrademode) enumeration.  
ExecMode | Integer | The symbol execution mode for the group. Passed in a value of the [EnExecutionMode (#enexecutionmode)](mt5-symbols/Enumerations.md#enexecutionmode) enumeration.  
FillFlags | Integer | Types of filling allowed for the symbol in this group. Passed as a value of the [EnFillingFlags (#enfillingflags)](mt5-symbols/Enumerations.md#enfillingflags) enumeration (sum of values of appropriate flags).  
ExpirFlags | Integer | Types of order expiration allowed for the symbol in this group. Passed as a value of the [EnExpirationFlags (#enexpirationflags)](mt5-symbols/Enumerations.md#enexpirationflags) enumeration (sum of values of appropriate flags).  
SpreadDiff | Integer | Difference between the symbol spread for the group and the default spread.  
SpreadDiffBalance | Integer | The balance of spread difference set for the group. The balance of spread difference is set a shift from the equal distribution of the spread difference value between Bid and Ask prices. For example, if the spread difference is equal to 4 and it is distributed as -2 Bid/+2 Ask, then the balance of spread difference value is 0. The -3 Bid/+1 Ask ratio corresponds to value -1, ratio -1 Bid/+3 Ask corresponds to value 1.  
StopsLevel | Integer | The price band, within which the group is not allowed to place stop orders for a symbol.  
FreezeLevel | Integer | The price band, within which it is not allowed to modify orders and positions for the group.  
VolumeMin | Integer | The minimum volume of trade operations for a symbol for the group. One unit corresponds to 1/10000 lot.  
VolumeMinExt | Integer | The minimum volume (with extended accuracy) of trade operations for a symbol for the group. One unit corresponds to 1/100000000 lot.  
VolumeMax | Integer | The maximum volume of trade operations for a symbol for the group. One unit corresponds to 1/10000 lot.  
VolumeMaxExt | Integer | The maximum volume (with extended accuracy) of trade operations for a symbol for the group. One unit corresponds to 1/100000000 lot.  
VolumeStep | Integer | The step of change of trade operations volume for a symbol for the group. One unit corresponds to 1/10000 lot.  
VolumeStepExt | Integer | The step of change of trade operations volume (with extended accuracy) for a symbol for the group. One unit corresponds to 1/100000000 lot.  
VolumeLimit | Integer | The maximum allowed aggregate volume of positions and orders for a symbol in one direction for this group. One unit corresponds to 1/10000 lot.  
VolumeLimitExt | Integer | The maximum aggregate volume (with extended accuracy) of positions and orders for a symbol for this group. One unit corresponds to 1/100000000 lot.  
MarginFlags | Integer | The additional modes of symbol margin checking for the group. Passed in a value of the [EnMarginFlags (#enmarginflags)](mt5-symbols/Enumerations.md#enmarginflags) enumeration.  
MarginInitial | Float | The size of initial symbol margin for the group.  
MarginMaintenance | Float | The size of symbol maintenance margin for the group.  
MarginLong | Float | The group margin ratio for long positions and orders for a symbol.  
MarginShort | Float | The group margin ratio for short positions and orders for a symbol.  
MarginLimit | Float | The group margin ratio of limit orders for a symbol.  
MarginStop | Float | The group margin ratio of stop orders for a symbol.  
MarginStopLimit | Float | The group margin ratio for stop-limit orders for a symbol.  
MarginHedged | Float | The hedged margin value.  
SwapMode | Integer | The swap calculation mode for a certain symbol for the group. Passed in a value of the [EnSwapMode (#enswapmode)](mt5-symbols/Enumerations.md#enswapmode) enumeration.  
SwapLong | Float | The long position swap for a symbol for the group.  
SwapShort | Integer | The short position swap for a symbol for the group.  
SwapYearDays | Integer | The number of days in a year used in calculating swap percent for a given group. Passed by the [EnSwapDays (#enswapdays)](mt5-symbols/Enumerations.md#enswapdays) enumeration value.  
SwapFlags | Integer | Additional swap settings by symbol for the given group. Passed by the [EnSwapFlags (#enswapflags)](mt5-symbols/Enumerations.md#enswapflags) enumeration value.  
SwapRateSunday | Float | Sunday swap multiplier in symbol settings for the given group.  
SwapRateMonday | Float | Monday swap multiplier in symbol settings for the given group.  
SwapRateTuesday | Float | Tuesday swap multiplier in symbol settings for the given group.  
SwapRateWednesday | Float | Wednesday swap multiplier in symbol settings for the given group.  
SwapRateThursday | Float | Thursday swap multiplier in symbol settings for the given group.  
SwapRateFriday | Float | Friday swap multiplier in symbol settings for the given group.  
SwapRateSaturday | Float | Saturday swap multiplier in symbol settings for the given group.  
RETimeout | Integer | Time in seconds during which the price issued by a dealer in the request execution mode is valid.  
IECheckMode | Integer | The mode of checking during instant execution set for a group. Passed in a value of the [EnInstantMode (#eninstantmode)](mt5-symbols/Enumerations.md#eninstantmode) enumeration.  
IETimeout | Integer | The maximum allowed difference between the time of arrival of the price, at which the client places an order, and the time of the last price. The timeout is specified in seconds.  
IESlipProfit | Integer | The maximum allowed slippage in the profitable direction during instant execution.  
IESlipLosing | Integer | The maximum allowed slippage in the loss direction during instant execution.  
IEVolumeMax | Integer | The maximum volume of a trade operation that can be executed in the instant execution mode. One unit corresponds to 1/10000 lot.  
IEVolumeMaxExt | Integer | The maximum volume (with extended accuracy) of a trade operation that can be executed in the instant execution mode. One unit corresponds to 1/100000000 lot.  
OrderFlags | Integer | The flags of order types that are allowed for the symbol. Passed in a value of the [EnOrderFlags (#enorderflags)](mt5-symbols/Enumerations.md#enorderflags) enumeration (sum of values of appropriate flags).  
MarginRateLiquidity | Float | The liquidity rate of the symbol for the group. It determines the amount of the current value of an asset for the specified financial instrument, which will be taken into account as collateral (accounted for in client's equity).  
REFlags | Integer | The flags of request execution for the group.  
  
> NULL value in the fields beginning from TradeMode means that the appropriate setting is inherited from the [base symbol](mt5-symbols.md).

```

---

<a id='backup-server-sql-export-mt5-groups-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-groups.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_groups

[Previous](mt5-symbols-sessions.md) | [Next](mt5-groups/Enumerations.md)

# mt5_groups

[Groups'](../../../Platform-Setup/Groups.md) configurations are exported to the table. The table contains the following fields:

Name | Type | Description  
Group_ID | Integer | Primary key. Unique group ID for more efficient request of the group data from the database. Assigned automatically during the export.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Group | String | The name of a group, including a path to it in accordance with the hierarchy.  
Server | Integer | The ID of the trade server, to which the group is linked.  
PermissionFlags | Integer | Flags of group permissions. Passed as a value of the [EnPermissionsFlags (#enpermissionsflags)](mt5-groups/Enumerations.md#enpermissionsflags) enumeration (sum of values of appropriate flags).  
AuthMode | Integer | Authorization mode for accounts in the group. Passed in a value of the [EnAuthMode (#enauthmode)](mt5-groups/Enumerations.md#enauthmode) enumeration.  
AuthPasswordMin | Integer | The minimum password length for accounts in the group.  
Company | String | Name of the company that services the group.  
CompanyPage | String | The website address of the company that services the group.  
CompanyEmail | String | The email address of the company that services the group.  
CompanySupportPage | String | The technical support website address of the company that services the group.  
CompanySupportEmail | String | The technical support email address of the company that services the group.  
CompanyCatalog | String | The name of the subdirectory that stores the templates of reports, emails, etc. for the company that services this group.  
Currency | String | The group deposit currency.  
CurrencyDigits | Integer | The number of digits after the decimal point in the group deposit currency.  
ReportsMode | Integer | Report generation modes. Passed in a value of the [EnReportsMode (#enreportsmode)](mt5-groups/Enumerations.md#enreportsmode) enumeration.  
ReportsFlags | Integer | Report sending options. Passed as a value of the [EnReportFlags (#enreportsflags)](mt5-groups/Enumerations.md#enreportsflags) enumeration (sum of values of appropriate flags).  
ReportsEmail | String | [The mail server](../../../Platform-Setup/Integrations/Mail-Servers.md) used for sending reports to clients from the group.  
ReportsSMTP | String | Address of SMTP server for sending reports. The field is obsolete and is not updated.  
ReportsSMTPLogin | String | A login for the authorization on the SMTP server that is used for sending reports. The field is obsolete and is not updated.  
NewsMode | Integer | The mode of news sending to the clients from the group. Passed in a value of the [EnNewsMode (#ennewsmode)](mt5-groups/Enumerations.md#ennewsmode) enumeration.  
NewsCategory | String | The categories of news received by the group. Use the backslash character "\" to specify subcategories.  
NewsLangs | Array of integer numbers | The array of languages, in which the group receives news. The language is specified in the LANGID format used in the [MS Windows](https://msdn.microsoft.com/en-us/library/windows/desktop/dd318693) (value from Prim.lang.identifier).  
MailMode | Integer | The mode of operation of the internal mail system for the group. Passed in a value of the [EnMailMode (#enmailmode)](mt5-groups/Enumerations.md#enmailmode) enumeration.  
TradeFlags | Integer | Trade options of the group. Passed as a value of the [EnTradeFlags (#entradeflags)](mt5-groups/Enumerations.md#entradeflags) enumeration (sum of values of appropriate flags).  
TradeInterestrate | Float | The annual interest rate on deposits of the group accounts.  
TradeVirtualCredit | Float | The amount of additional funds that a brokerage company can provide to a client for opening a position with a volume larger than allowed by the client's current funds.  
MarginFreeMode | Integer | The mode of using of floating profit/loss in the free margin. Passed in a value of the [EnFreeMarginMode (#enfreemarginmode)](mt5-groups/Enumerations.md#enfreemarginmode) enumeration.  
MarginSOMode | Integer | The mode of checking the levels of Stop Out and Margin Call. Passed in a value of the [EnStopOutMode (#enstopoutmode)](mt5-groups/Enumerations.md#enstopoutmode) enumeration.  
MarginCall | Float | The level of Margin Call. Units are determined by the MarginSOMode parameter.  
MarginStopOut | Float | The level of Stop Out. Units are determined by the MarginSOMode parameter.  
MarginFreeProfitMode | Integer | The mode of using the profit/loss fixed during a trade day in the free margin.  
MarginMode | Integer | The risk management model of the group.  
MarginFlags | Integer | Margin calculation flags.  
DemoLeverage | Integer | The default credit leverage for demo accounts opened in the group.  
DemoDeposit | Float | The default amount of deposit for demo accounts opened in the group.  
LimitHistory | Integer | The maximum number of days, for which the group can request data on conducted trade operation. Passed in a value of the [EnHistoryLimit (#enhistorylimit)](mt5-groups/Enumerations.md#enhistorylimit) enumeration.  
LimitOrders | Integer | The maximum number of orders that can be simultaneously placed by an account from this group.  
LimitSymbols | Integer | The maximum number of symbols, for which an account can simultaneously receive quotes.  
LimitPositions | Integer | The maximum number of open positions which the client can have on the account at the same time.  
LimitPositionsVolume | Float | Currently the field is not used.  
TradeTransferMode | Integer | The mode of transferring funds between accounts.

```

---

<a id='backup-server-sql-export-mt5-holidays-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-holidays.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_holidays

[Previous](mt5-daily-positions.md) | [Next](mt5-network.md)

# mt5_holidays

Data about [holidays](../../../Platform-Setup/Holidays.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Year | Integer | The year of a holiday. 0 stands for yearly holidays.  
Month | Integer | Month of a holiday (1 — January, 12 — December).  
Day | Integer | Day of a holiday.  
From | Integer | Holiday start time. Specified in a number of minutes from 00:00. For example, 600 corresponds to 10:00.  
To | Integer | Holiday end time. Specified in a number of minutes from 00:00. For example, 1200 corresponds to 20:00.  
Description | String | Holiday description (no more than 128 symbols).  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Mode | Integer | Holiday mode. 0 — holiday disabled, 1 — enabled.  
Symbols | String | The list of financial instruments or their groups, for which a holiday is valid. Instruments and groups are separated by comma, for example: "EURUSD,CFD\*".

```

---

<a id='backup-server-sql-export-mt5-managers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-managers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_managers

[Previous](mt5-commissions-tiers.md) | [Next](mt5-clients.md)

# mt5_managers

Data about [manager accounts](../../../Platform-Setup/Managers.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Initial key. The user login, based on which the manager account is created.  
Timestamp | Integer | A unique values within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has changed.  
Name | String | The name of the manager.  
Mailbox | String | The name of the manager's mailbox in the internal mailing system.  
Server | Integer | The ID of the trade server to which the manager belongs.  
RequestLimitLogs | Integer | The time period of system logs that are available to a manager:

  * 0 — unlimited
  * 1 — 1 month
  * 2 — 3 months
  * 3 — 6 months
  * 4 — 1 year
  * 5 — 2 years
  * 6 — 3 years

  
RequestLimitReports | Integer | The time period of reports that are available to a manager:

  * 0 — unlimited
  * 1 — 1 month
  * 2 — 3 months
  * 3 — 6 months
  * 4 — 1 year
  * 5 — 2 years
  * 6 — 3 years

  
Groups | String | The list of groups processed by the manager. The groups are separated by commas, for example: "demo\forex-netting,demo\forex-netting".  
Access | String | The list of IP addresses, from which a manager is allowed to connect to the platform. Example: 192.168.0.1-192.168.0.10,192.168.0.12-192.168.0.20.  
Further fields in the table describe [manager permissions (#permissions)](../../../Platform-Setup/Managers.md#permissions). A value of 1 means that the right is granted to the manager, 0 means no permission.  
Right_Admin | Integer | Connection using the administrator terminal.  
Right_Manager | Integer | Connection using the manager terminal.  
Right_Cfg_Servers | Integer | Network configuration  
Right_Cfg_Access | Integer | Configuration of the list of IP access.  
Right_Cfg_Time | Integer | Configuration of the server working time.  
Right_Cfg_Holidays | Integer | Configuration of holidays.  
Right_Cfg_Groups | Integer | Configuration of groups.  
Right_Cfg_Managers | Integer | Configuration of manager rights.  
Right_Cfg_Requests | Integer | Configuration of the routing table.  
Right_Cfg_Gateways | Integer | Configuration of gateways.  
Right_Cfg_Plugins | Integer | Configuration of plugins.  
Right_Cfg_Datafeeds | Integer | Configuration of data feeds.  
Right_Cfg_Reports | Integer | Configuration of reports.  
Right_Cfg_Symbols | Integer | Configuring the symbols.  
Right_Cfg_Hst_Sync | Integer | Configuration of synchronization.  
Right_Cfg_ECN | Integer | ECN configuration.  
Right_Cfg_VPS | Integer | Configuring Sponsored VPS for traders.  
Right_Cfg_Web_Services | Integer | Configuring integration with web services: SSL certificates and addresses for callback requests.  
Right_Cfg_Funds | Integer | Configuring investment funds in the Administrator terminal  
Right_Cfg_Messengers | Integer | Configuring integration with SMS providers and messengers in the Administrator terminal  
Right_Cfg_KYC | Integer | Configuring integration with KYC services in the Administrator terminal  
Right_Cfg_Automations | Integer | Configuring automatic actions for specified scenarios in the Administrator terminal.  
Right_Cfg_Allocations | Integer | Accessing the Allocations section of the Administrator terminal. The section allows configuring groups, in which traders are able to open demo and preliminary real accounts directly from client terminals.  
Right_Cfg_Corporates | Integer | Access to [corporate link](../../../Platform-Setup/Accounts/Corporate-Links.md) settings.  
Right_Cfg_Payments | Integer | Configuring integration with payment systems.  
Right_Cfg_Mails | Integer | Configuring integration with email services in the Administrator terminal.  
Right_Srv_Journals | Integer | Access to server journals.  
Right_Srv_Reports | Integer | Receiving automatic server reports.  
Right_Charts | Integer | Editing history data on the server.  
Right_Email | Integer | Sending internal emails.  
Right_News | Integer | Permission to send newsletters. An administrator or manager can only send newsletters if his or her account belongs to a group created on the main trade server.  
Right_Export | Integer | Permission to export data.  
Right_Techsupport | Integer | Access to the technical support tab in the administrator and manager terminals. The permission is obsolete and is no longer used.  
Right_Market | Integer | Permission to access the Market of applications in the MetaTrader 5 Administrator. The permission is obsolete and is no longer used.  
Right_Accountant | Integer | Permission to work with funds on accounts.  
Right_Acc_Read | Integer | Access to accounts.  
Right_Acc_Details_Name | Integer | Access to name details in [accounts (#personal)](../../../Platform-Setup/Accounts/Editing-Account.md#personal).  
Right_Acc_Details_Location | Integer | Access to location data in accounts: country, city, region, zip code.  
Right_Acc_Details_Address | Integer | Access to address details in [accounts (#personal)](../../../Platform-Setup/Accounts/Editing-Account.md#personal).  
Right_Acc_Details_ID | Integer | Access to data on document numbers in accounts.  
Right_Acc_Details_EMail | Integer | Access to email details in accounts.  
Right_Acc_Details_Phone | Integer | Access to phone details in accounts.  
Right_Acc_Details_General | Integer | Access to other data in accounts (language, status, comment, MetaQuotes ID, etc.).  
Right_Acc_Technical | Integer | When combined with the "[Show to regular managers (#limits)](../../../Platform-Setup/Accounts/Editing-Account.md#limits)" permission, provides greater convenience when working with various testing and technical accounts. Disable the "Enable visibility for regular managers" permission for all technical accounts, and then disable access to technical accounts for the managers who do not configure the platform. Otherwise, such technical accounts can be confusing for managers working with clients.  
Right_Acc_Tech_Modify | Integer | Allows enabling and disabling the "[Show to regular managers (#limits)](../../../Platform-Setup/Accounts/Editing-Account.md#limits)" and "[Include in server reports (#limits)](../../../Platform-Setup/Accounts/Editing-Account.md#limits)" options for a trading account. Without this permission, the manager can only see the states of the relevant options, without the ability to change them (read-only).  
Right_Acc_Manager | Integer | Account editing.  
Right_Acc_Delete | Integer | Deleting client accounts via the administrator and manager terminals, and via the Manager API. The Right_Acc_Manager permission is required in order to enable this permission.  
Right_Acc_Online | Integer | Getting the current client connections.  
Right_Confirm_Actions | Integer | By default the manager terminal displays a confirmation dialog when performing balance operations on client accounts and closing multiple orders. A manager needs to enter a randomly generated sequence of characters in order to confirm the appropriate action. If this permission is disabled, the above actions will be performed immediately without any confirmation.  
Right_Notifications | Integer | Permission to send push notifications to clients' mobile devices from the manager terminal. Messages are sent based on MetaQuotes ID, which is a unique user identifier. To obtain the ID, a user needs to install MetaTrader 5 Mobile for [iPhone](https://download.mql5.com/cdn/mobile/mt5/ios?hl=ru&utm_campaign=download&utm_source=metatrader5.help "iPhone") and [Android](https://download.mql5.com/cdn/mobile/mt5/android?hl=ru&utm_campaign=download&utm_source=metatrader5.help "Android"). For more information please read the MetaTrader 5 Manager user guide.  
Right_Trades_Read | Integer | Viewing trading orders, deals and positions. This right affects the possibility to enable Right_Trades_Manager and Right_Trades_Dealer permissions.  
Right_Trades_Manager | Integer | Changing any fields of orders, deals and positions in the administrator terminal, and changing position open prices in the manager terminal.  
Right_Trades_Delete | Integer | Deleting any orders, deals and positions via the administrator and manager terminals, and via the Manager API. The Right_Trades_Manager permission is required in order to enable this permission.  
Right_Trades_Dealer | Integer | The possibility to perform trading and dealing operations in the manager terminal.  
Right_Trades_Supervisor | Integer | This right allows the manager to view the entire queue of requests received from groups of clients available to the manager, as well as to track processing of requests by other dealers in the manager terminal. Manager works in the "Supervisor" mode without connecting as a dealer in the manager terminal. After connecting as a dealer, the manager will only see the requests that are forwarded to him or her for processing in accordance with the routing rules.  
Right_Quotes_Raw | Integer | If this permission is enabled, the "Show raw quotes" command will appear in the context menu of the Market Watch window in the manager terminal. With this permission, the manager can view quotes without considering spread difference settings set for the manager group.  
Right_Quotes | Integer | Permission to throw in quotes  
Right_Symbol_Details | Integer | Permission to change spread and execution mode.  
Right_Risk_Manager | Integer | Permission to receive information about client's aggregate positions and company's coverage positions.  
Right_Group_Margin | Integer | Permission to configure margin for groups in MetaTrader 5 Manager.  
Right_Group_Commission | Integer | Permission to configure commissions for groups in MetaTrader 5 Manager.  
Right_Reports | Integer | Permission to request and receive various reports on client operations.  
Right_Finteza_Access | Integer | Access to the [Finteza Analytics](../../../Platform-Setup/Integrations.md) section.  
Right_Finteza_Websites | Integer | View Finteza data relating to websites in the Analytics section of the Manager terminal.  
Right_Finteza_Campaigns | Integer | View Finteza data relating to marketing campaigns in the Analytics section of the Manager terminal.  
Right_Finteza_Reports | Integer | The permission is currently not used.  
Right_Clients_Access | Integer | Access to the Clients section in the Administrator and Manager terminals.  
Right_Clients_Create | Integer | Permission to create new client records manually.  
Right_Clients_Edit | Integer | Permission to edit client data, except for documents.  
Right_Clients_Delete | Integer | PermiRight_Clients_KYCssion to delete client records.  
Right_Clients_KYC | Integer | Permission to launch automated validation of client data via [integrated KYC services](../../../Platform-Setup/Integrations/KYC.md). The permission affects the launching of verification from Manager and Administrator terminals, as well as from API.  
Right_Documents_Access | Integer | Permission to view client documents.  
Right_Documents_Create | Integer | Permission to add general information about documents in client records.  
Right_Documents_Edit | Integer | Permission to edit general information about documents in client records.  
Right_Documents_Delete | Integer | Permission to delete general information about documents from client records.  
Right_Documents_Files_Add | Integer | Permission to add document files in client records.  
Right_Documents_Files_Delete | Integer | Permission to delete document files from client records.  
Right_Comments_Access | Integer | Permission to read comments to clients and their documents.  
Right_Comments_Create | Integer | Permission to write comments to clients and their documents.  
Right_Comments_Delete | Integer | Permission to delete comments to clients and their documents.  
Right_Admin_Computer | Integer | Access to the server machine administration menu in the Network section of the Administrator terminal  
Right_Subscriptions_View | Integer | Permission to view existing settings in the Subscriptions section in the Administrator terminal, as well as access to subscription statistics.  
Right_Subscriptions_Edit | Integer | Permission to create, edit and remove settings in the Subscriptions section of the Administrator terminal.  
Right_Payments_Access | Integer | Permission to view current and processed [payments](../../../Platform-Setup/Payments.md) and payment accounts.  
Right_Payments_Process | Integer | [Permission to confirm and reject payments](../../../Platform-Setup/Payments/Processing.md) processed manually via the Manager terminal.  
Right_Payments_Edit | Integer | Permission to edit current and processed payments and payment accounts.  
Right_Payments_Delete | Integer | Permission to delete current and processed payments and payment accounts.

```

---

<a id='backup-server-sql-export-mt5-network-access-servers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-network-access-servers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_network_access_servers

[Previous](mt5-network.md) | [Next](mt5-network-history-servers.md)

# mt5_network_access_servers

Data on the [access servers settings](../../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Server ID.  
Priority | Integer | Base priority of the access server from 0 to 15. The special priority 255 (idle) designed to create backup access servers is possible as well.  
AntifloodEnable | Integer | Antiflood control: 0 — disabled, 1 — enabled.  
AntifloodConnects | Integer | The maximum number of connections from one IP address for a certain period of time, after which the address is temporarily blocked.  
AntifloodErrors | Integer | The maximum number of incorrect connections, after which the IP address is temporarily blocked.  
NewsMaxCount | Integer | The maximum number of news that can be stored on the access server.  
BalancingConnections | Integer | The current number of connections.  
BalancingPriority | Integer | The current priority of the access server.  
AccessMask | Integer | The allowed types of connection to the access server. Set as a sum of flag values:

  * 1 — client connections.
  * 2 — manager connections.
  * 4 — administrator connections.
  * 8 — connections via the Client API.
  * 16 — connections via the Manager API.


  * 32 — connections via the Web API.

For example, the value of 63 means that all connection types are allowed.  
AccessFlags | Integer | Additional server accessing flags:

  * 1 — the access server is [hidden from all terminals (#permissions)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#permissions) but is available for connection.

  
Servers | String | IDs of trade servers (comma-separated), the connection to which is implemented through this access server.

```

---

<a id='backup-server-sql-export-mt5-network-backup-folders-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-network-backup-folders.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_network_backup_folders

[Previous](mt5-network-backup-servers.md) | [Next](mt5-firewall.md)

# mt5_network_backup_folders

Data on the [backed up custom directories (#folders)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#folders) is exported to this table. The table contains the following fields:

Name | Type | Description  
Folder_ID | Integer | Unique entry ID.  
Login | Integer | Backup server ID.  
Folder | String | The path to the backed up folder relative to the backup server installation directory.  
Masks | String | List of copied files (comma-separated). Files can be specified by masks.  
Filter | String | List of ignored files (comma-separated). Files can be specified by masks.

```

---

<a id='backup-server-sql-export-mt5-network-backup-servers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-network-backup-servers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_network_backup_servers

[Previous](mt5-network-trade-servers.md) | [Next](mt5-network-backup-folders.md)

# mt5_network_backup_servers

Data on the [backup servers settings](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Server ID.  
PairrServer | Integer | ID of the server to backup.  
BackupFlags | Integer | [Backup settings (#backup)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#backup). The settings are specified as a sum of flags:

  * 1 — enables backup.
  * 2 — enables the backup of tick data.
  * 4 — enables the possibility to use the server for the automatic Failover, with which the system switches to this backup server.
  * 8 — enables synchronization of logs with the primary server.

  
BackupPath | String | The path to save backups.  
BackupPeriod | Integer | Backup frequency:

  * 0 — no periodic backups
  * 1 — every 15 minutes
  * 2 — every 30 minutes
  * 3 — every hour
  * 4 — every 4 hours
  * 5 — every day

  
BackupTtl | Integer | Period to keep backups:

  * 1 — one day
  * 2 — three days
  * 3 — one week
  * 4 — one month
  * 5 — three months
  * 6 — six months

  
BackupTimeFull | Integer | Time of creating full backup copies in minutes since 00:00.  
BackupLastStartup | DateTime | The last backup copy creation time when launching the server in the YYYY-MM-DD HH:MM:SS.MSC format.  
BackupLastFull | DateTime | The last full backup copy creation time in the YYYY-MM-DD HH:MM:SS.MSC format.  
BackupLastArchive | DateTime | The last increment backup copy creation time in the YYYY-MM-DD HH:MM:SS.MSC format.  
BackupLastSync | DateTime | The time of the last successful synchronization with the backed up server in the YYYY-MM-DD HH:MM:SS.MSC format.  
SqlMode | Integer | Mode of exporting data to an SQL database:

  * 0 — export disabled
  * 1 — export to Microsoft SQL Server
  * 2 — export to FireBird
  * 3 — export to MySQL
  * 4 — export to Oracle

  
SqlServer | String | The address of the server the database is installed on.  
SqlFolder | String | The name of the SQL database the data is exported to.  
SqlFlags | Integer | Additional settings of data export to an SQL database. Defined by the sum of flags: 1 — export trade history to separate tables. 2 — do not export accounts and trade operations of demo groups For example, the value of 3 means that both settings are enabled.  
SqlPeriod | Integer | The frequency of price and profit data export.  
SQLExportLastSync | Integer | The time of the last full synchronization of databases and platform configurations with the SQL database. Specified in seconds since 01.01.1970. If data export is disabled or synchronization is in progress, the value is 0. The full synchronization is launched when a backup server is started or after connection to the SQL database or to the trading server is lost. After synchronization, the SQL database is updated in real time in accordance with the transactions of changes in the platform databases.

```

---

<a id='backup-server-sql-export-mt5-network-history-servers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-network-history-servers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_network_history_servers

[Previous](mt5-network-access-servers.md) | [Next](mt5-network-trade-servers.md)

# mt5_network_history_servers

Data on the [history server settings](../../../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Server ID.  
DatafeedsTimeout | Integer | Timeout of data feeds before switching to other ones. Specified in seconds.  
NewsMax | Integer | The maximum number of news that can be stored on the history server.

```

---

<a id='backup-server-sql-export-mt5-network-trade-servers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-network-trade-servers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_network_trade_servers

[Previous](mt5-network-history-servers.md) | [Next](mt5-network-backup-servers.md)

# mt5_network_trade_servers

Data on the [trade servers settings](../../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Server ID.  
DemoMode | Integer | Mode of demo account allocation:

  * 0 — creation of demo accounts is disabled.
  * 1 — prolong the period of demo accounts after connection.
  * 2 — demo accounts with a fixed expiration date.

  
DemoPeriod | Integer | The validity of demo accounts.  
OvernightMode | Integer | The overnight mode.  
OvernightTime | Integer | The time of transition to the next day in minutes after 00:00.  
OvernightTimeLast | DateTime | The time of the last transition to the next day in the YYYY-MM-DD HH:MM:SS.MSC format.  
OvernightTimePrev | DateTime | The time of the penultimate transition to the next day in the YYYY-MM-DD HH:MM:SS.MSC format.  
OvernightDays | Integer | Schedule of operations related to the trading day closure. Set as a sum of flags:

  * 0x00000001 — Sunday
  * 0x00000002 — Monday
  * 0x00000004 — Tuesday
  * 0x00000008 — Wednesday
  * 0x00000010 — Thursday
  * 0x00000020 — Friday
  * 0x00000040 — Saturday

Further flags specify days, on which swaps are charged:

  * 0x00000080 — Sunday
  * 0x00000100 — Monday
  * 0x00000200 — Tuesday
  * 0x00000400 — Wednesday
  * 0x00000800 — Thursday
  * 0x00001000 — Friday
  * 0x00002000 — Saturday

  
OvermonthMode | Integer | The overmonth mode:

  * 0 — on the last day of the month.
  * 1 — on the first day of the month.

  
OvermonthTimeLast | DateTime | The time of the last transition to the next month in the YYYY-MM-DD HH:MM:SS.MSC format.  
OvermonthTimePrev | DateTime | The time of the penultimate transition to the next month in the YYYY-MM-DD HH:MM:SS.MSC format.  
TotalUsers | Integer | The total number of client accounts on the trade server.  
TotalUsersReal | Integer | The total number of real clients on the trade server.  
TotalDeals | Integer | The total number of deals executed on the trade server.  
TotalOrders | Integer | The total number of active orders placed on the trade server.  
TotalOrdersHistory | Integer | The total number of orders in the history on the trade server.  
TotalPositions | Integer | The total number of positions on the trade server.  
LoginsRange | String | Account ranges on the trade server. For example, 1000-1000000,2000001-2999001.  
LoginsRangeUsed | String | Ranges of actually used logins from LoginsRange. For example, 1000-1004,0-0.  
OrdersRange | String | Order ticket ranges on the trade server. For example, 1-1000000,2000001-2999001.  
OrdersRangeUsed | String | Ranges of actually used order tickets from OrdersRange. For example, 1-53,0-0.  
DealsRange | String | Trade ticket ranges on the trade server. For example, 1-1000000,2000001-2999001.  
DealsRangeUsed | String | Ranges of actually used trade tickets and DealsRange. For example, 1-56,0-0.

```

---

<a id='backup-server-sql-export-mt5-network-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-network.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_network

[Previous](mt5-holidays.md) | [Next](mt5-network-access-servers.md)

# mt5_network

Data on the platform [servers' general settings](../../../Platform-Setup/Network-cluster/Configuring-Servers.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Server ID.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Type | Integer | Server type.  
Name | String | Server name.  
Address | String | Server address.  
Port | String | Server port.  
Adapter | String | Name of the currently used network controller.  
ServiceTime | Integer | Service time (time of optimization) when various operations aimed at increasing the performance and reliability of the platform are conducted. Specified in a number of minutes from 00:00. For example, 600 corresponds to 10:00.  
FailoverMode | Integer | Automatic [failover modes](../Switching-to.md): 

  * 0 — failover disabled
  * 1 — server is unavailable for most access servers
  * 2 — server is unavailable for all access servers

  
FailoverTimeout | Integer | Time in seconds, during which the server should be unavailable for monitoring servers to start switching to the backup server.  
Adapters | String | List of all available network controllers on PC (comma-separated).  
Addresses | String | List of available addresses for outgoing connections from this server (comma-separated).  
Binds | String | List of listen addresses (comma-separated).  
Points | String | List of public access points, via which connections are to be accepted.  
Version | Integer | Server version.  
Build | Integer | Server build.  
BuildDate | String | Server build date.  
SysConnection | Integer | Status of a server connection to the main trade server.  
SysLastBoot | DateTime | Time of the last server boot in the YYYY-MM-DD HH:MM:SS.MSC format.  
SysOsName | String | Operating system of the computer running the server.  
SysCpuName | String | Processor type of the computer that is running the server.  
SysCpuNumber | Integer | Number of CPU cores.  
SysBits | Integer | Operating system bits:

  * 32 — 32 bits
  * 64 — 64 bits
  * 0 — other

  
SysMemoryTotal | Integer | The total amount of RAM in megabytes.  
SysMemoryFree | Integer | The amount of free memory in megabytes.  
SysMemoryCritical | Integer | The critical amount of free memory in megabytes.  
SysHddSize | Integer | Total volume of a disk in megabytes.  
SysHddFree | Integer | Free memory on the disk in megabytes.  
SysHddCritical | Integer | Critical amount of free memory on the disk in megabytes.  
SysHddFragmentation | Integer | The current level of fragmentation of the server files in percentage.  
SysHddFragCritical | Integer | The critical level of fragmentation of the server files in percentage.  
SysDefragRecommend | Integer | The flag indicating that the operating system recommends defragmenting the disk:

  * 0 — no recommendation
  * 1 — recommendation is present

  
SysHddReadSpeed | Integer | The current speed of data reading from the disk in megabytes per second.  
SysHddReadCritical | Integer | The critical speed of data reading from the disk in megabytes per second.  
SysHddWriteSpeed | Integer | The current speed of saving data to the disk in megabytes per second.  
SysHddWriteCritical | Integer | The critical speed of saving data to the disk in megabytes per second.  
PerfConnectsMax | Integer | The maximum number of simultaneous connections to a server that has been achieved during the day.  
PerfConnectsCritical | Integer | Critical number of simultaneous connections to the server.  
PerfCpuMax | Integer | Get the maximum level of CPU usage in percentage for the current day.  
PerfCpuCritical | Integer | Get the critical level of CPU usage in percentage.  
PerfMemoryMin | Integer | The minimum size of free random access and virtual memory in megabytes per day.  
PerfMemoryCritical | Integer | The critical amount of free memory in megabytes.  
PerfMemBlockMin | Integer | The minimum value of the maximum memory block in megabytes per day.  
PerfMemBlockCritical | Integer | The critical value of the maximum memory block in megabytes per day.  
PerfNetworkMax | Integer | The maximum level of network usage in kilobytes per second for the current day.  
PerfNetworkCritical | Integer | The critical level of network usage in kilobytes per second.  
PerfSocketsMax | Integer | The maximum number of active sockets per day.  
PerfSocketsCritial | Integer | The critical number of active sockets.

```

---

<a id='backup-server-sql-export-mt5-orders-history-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-orders-history.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_orders_history

[Previous](mt5-orders/Enumerations.md) | [Next](mt5-positions.md)

# mt5_orders_history

Data on closed [orders](../../../Platform-Setup/Orders.md) is exported to the table. If "[Export history orders and deals into separate tables by years" (#sql-settings)](../../../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#sql-settings) option is enabled in settings, closed orders for each year are exported to a separate table. A year is specified in the table heading, for example, mt5_orders_2012. If the option is disabled, all closed orders are exported to a single mt5_orders_history table.

The table contains the following fields:

Name | Type | Description  
Order | Integer | Primary key. Order ticket.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
ExternalID | String | The order ID in external trading systems.  
Login | Integer | The login of the client, to whom the order belongs.  
Dealer | Integer | The login of a dealer, who has processed an order.  
Symbol | String | The symbol of an order.  
Digits | Integer | The number of decimal places in the price of an order.  
DigitsCurrency | Integer | The number of decimal places the deposit currency of the client who has placed the order.  
ContractSize | Float | The contract size of the symbol, for which an order was placed.  
State | Integer | The current state of an order. Passed as a value of the [EnOrderMode (#enorderstate)](mt5-orders/Enumerations.md#enorderstate) enumeration.  
Reason | Integer | The reason for placing the order. Passed as a value of the [EnOrderReason (#enorderreason)](mt5-orders/Enumerations.md#enorderreason) enumeration.  
TimeSetup | DateTime | Order placement time in the YYYY-MM-DD HH:MM:SS format.  
TimeSetupMsc | Integer | Order placement time in milliseconds in the YYYY-MM-DD HH:MM:SS.MS format.  
TimeExpiration | DateTime | Order expiration time in the YYYY-MM-DD HH:MM:SS format.  
TimeDone | DateTime | Order execution time in the YYYY-MM-DD HH:MM:SS format.  
TimeDoneMsc | Integer | Order execution time in milliseconds in the YYYY-MM-DD HH:MM:SS.MS format.  
Type | Integer | Order type. Passed as a value of the [EnOrderType (#enordertype)](mt5-orders/Enumerations.md#enordertype) enumeration.  
TypeFill | Integer | Order filling type. Passed as a value of the [EnOrderFilling (#enorderfilling)](mt5-orders/Enumerations.md#enorderfilling) enumeration.  
TypeTime | Integer | Order expiration type. Passed in a value of the [EnOrderTime (#enordertime)](mt5-orders/Enumerations.md#enordertime) enumeration.  
PriceOrder | Float | Order price.  
PriceTrigger | Float | The order triggering price.  
PriceCurrent | Float | The current price of the symbol, for which an order has been placed.  
PriceSL | Float | The Stop Loss level of an order.  
PriceTP | Float | The Take Profit level of an order.  
VolumeInitial | Integer | The initial order volume. One unit corresponds to 1/10000 lot.  
VolumeInitialExt | Integer | The initial order volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeCurrent | Integer | The current unfilled volume of an order. One unit corresponds to 1/10000 lot.  
VolumeCurrentExt | Integer | The current unfilled order volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
ExpertID | Integer | The ID of the Expert Advisor that has placed the order.  
PositionID | Integer | The position ID (ticket) set in the order.  
PositionByID | Integer | The opposite position ID (ticket) set in the order. The property is set for Close By operations ([OP_CLOSE_BY (#enordertype)](mt5-orders/Enumerations.md#enordertype)). The ticket of the position that is closed by the opposite one is set in PositionID.  
Comment | String | A comment to an order.  
ActivationMode | Integer number | Order activation type. Passed in a value of the [EnOrderActivation (#enorderactivation)](mt5-orders/Enumerations.md#enorderactivation) enumeration.  
ActivationTime | DateTime | Order activation time in the YYYY-MM-DD HH:MM:SS format.  
ActivationPrice | Fractional number | The price, at which the order was activated.  
ActivationFlags | Integer number | Order activation flags. Passed as a value of the [EnTradeActivationFlags (#entradeactivationflags)](mt5-orders/Enumerations.md#entradeactivationflags) enumeration (sum of values of appropriate flags).  
RateMargin | Fractional number | The rate of conversion of the margin currency of the symbol to the deposit currency of the user, which is used when calculating the margin requirements for the order.  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{pos:0,app_id:1,valInt:500,valUInt:500,valDbl:0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.

```

---

<a id='backup-server-sql-export-mt5-orders-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-orders.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_orders

[Previous](mt5-users/Enumerations.md) | [Next](mt5-orders/Enumerations.md)

# mt5_orders

Data on open [orders](../../../Platform-Setup/Orders.md) is exported to the table. The table contains the following fields:

Name | Type | Description  
Order | Integer | Primary key. Order ticket.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
ExternalID | String | The order ID in external trading systems.  
Login | Integer | The login of the client, to whom the order belongs.  
Dealer | Integer | The login of a dealer, who has processed an order.  
Symbol | String | The symbol of an order.  
Digits | Integer | The number of decimal places in the price of an order.  
DigitsCurrency | Integer | The number of decimal places the deposit currency of the client who has placed the order.  
ContractSize | Float  | The contract size of the symbol, for which an order was placed.  
State | Integer | The current state of an order. Passed as a value of the [EnOrderMode (#enorderstate)](mt5-orders/Enumerations.md#enorderstate) enumeration.  
Reason | Integer | The reason for placing the order. Passed as a value of the [EnOrderReason (#enorderreason)](mt5-orders/Enumerations.md#enorderreason) enumeration.  
TimeSetup | DateTime | Order placement time in the YYYY-MM-DD HH:MM:SS format.  
TimeSetupMsc | DateTime | Order placement time in milliseconds in the YYYY-MM-DD HH:MM:SS.MS format.  
TimeExpiration | DateTime | Order expiration time in the YYYY-MM-DD HH:MM:SS format.  
TimeDone | DateTime | Order execution time in the YYYY-MM-DD HH:MM:SS format.  
TimeDoneMsc | DateTime | Order execution time in milliseconds in the YYYY-MM-DD HH:MM:SS.MS format.  
ModifyFlags | Integer | The order modification flags. Passed as a value of the [EnTradeModifyFlags (#entrademodifyflags)](mt5-orders/Enumerations.md#entrademodifyflags) enumeration (sum of values of appropriate flags).  
Type | Integer | Order type. Passed as a value of the [EnOrderType (#enordertype)](mt5-orders/Enumerations.md#enordertype) enumeration.  
TypeFill | Integer | Order filling type. Passed as a value of the [EnOrderFilling (#enorderfilling)](mt5-orders/Enumerations.md#enorderfilling) enumeration.  
TypeTime | Integer | Order expiration type. Passed in a value of the [EnOrderTime (#enordertime)](mt5-orders/Enumerations.md#enordertime) enumeration.  
PriceOrder | Float  | Order price.  
PriceTrigger | Float | The order triggering price.  
PriceCurrent | Float | The current price of the symbol, for which an order has been placed.  
PriceSL | Float | The Stop Loss level of an order.  
PriceTP | Float | The Take Profit level of an order.  
VolumeInitial | Integer | The initial order volume. One unit corresponds to 1/10000 lot.  
VolumeInitialExt | Integer | The initial order volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeCurrent | Integer | The current unfilled volume of an order. One unit corresponds to 1/10000 lot.  
VolumeCurrentExt | Integer | The current unfilled order volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
ExpertID | Integer | The ID of the Expert Advisor that has placed the order.  
PositionID | Integer | The position ID (ticket) set in the order.  
PositionByID | Integer | The opposite position ID (ticket) set in the order. The property is set for Close By operations ([OP_CLOSE_BY (#enordertype)](mt5-orders/Enumerations.md#enordertype)). The ticket of the position that is closed by the opposite one is set in PositionID.  
Comment | String | A comment to an order.  
ActivationMode | Integer | Order activation type. Passed in a value of the [EnOrderActivation (#enorderactivation)](mt5-orders/Enumerations.md#enorderactivation) enumeration.  
ActivationTime | DateTime | Order activation time in the YYYY-MM-DD HH:MM:SS format.  
ActivationPrice | Float | The price, at which the order was activated.  
ActivationFlags | Integer | Order activation flags. Passed as a value of the [EnTradeActivationFlags (#entradeactivationflags)](mt5-orders/Enumerations.md#entradeactivationflags) enumeration (sum of values of appropriate flags).  
RateMargin | Float | The rate of conversion of the margin currency of the symbol to the deposit currency of the user, which is used when calculating the margin requirements for the order.  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{pos:0,app_id:1,valInt:500,valUInt:500,valDbl:0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.

```

---

<a id='backup-server-sql-export-mt5-plugin-params-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-plugin-params.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_plugin_params

[Previous](mt5-plugins.md) | [Next](mt5-time.md)

# mt5_plugin_params

Data about [additional plugin settings (#module)](../../../Platform-Setup/Plugins.md#module) is exported to this table. The table contains the following fields:

Name | Type | Description  
ParamID | String | The unique identifier of the parameter.  
Plugin | String | The name of the plugin, to which the setting applies.  
Server | Integer | The ID of the trade server, for which the plugin is configured.  
Type | Integer | Parameter type:

  * 0 — string
  * 1 — integer
  * 2 — floating-point number
  * 3 — time
  * 4 — date
  * 5 — date and time
  * 6 — list of groups
  * 7 — list of symbols

  
Name | String | The name of the parameter.  
Value | String | The value of the parameter.

```

---

<a id='backup-server-sql-export-mt5-plugins-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-plugins.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_plugins

[Previous](mt5-report-params.md) | [Next](mt5-plugin-params.md)

# mt5_plugins

Data about [plugin settings](../../../Platform-Setup/Plugins.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Name | String | The name of the plugin configuration.  
Server | Integer | The ID of the trade server, for which the plugin is configured.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Module | String | The name of the plugin module.  
Enable | Integer | Plugin operation mode: 0 — disabled, 1 — enabled.  
Flags | Integer | Plugin operation flags:

  * 0 — no flags
  * 1 — permission to configure the plugin from a manager terminal
  * 2 — the profiling mode enabled



```

---

<a id='backup-server-sql-export-mt5-positions-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-positions.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_positions

[Previous](mt5-orders-history.md) | [Next](mt5-positions/Enumerations.md)

# mt5_positions

Data on positions is exported to the table. The table contains the following fields:

Name | Type | Description  
Position_ID | Integer | Primary key. Internal position identifier used by the backup server to export data. Use the Position field to identify positions in your reports ans databases. The Position field contains the real identifier (ticket) assigned to the position in MetaTrader 5. The Position_ID field is only used for internal purposes and is not related with trading operation tickets.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Login | Integer | The login of the client, to whom the trade position belongs.  
Symbol | String | The symbol of a trade position.  
Action | Integer | Position type. Passed in a value of the [EnPositionAction (#enpositionaction)](mt5-positions/Enumerations.md#enpositionaction) enumeration.  
Digits | Integer | The number of decimal places in the price of a position.  
DigitsCurrency | Integer | The number of decimal places the deposit currency of the client who has opened the position.  
Reason | Integer | The reason for position opening. Passed in a value of the [EnPositionReason (#enpositionreason)](mt5-positions/Enumerations.md#enpositionreason) enumeration.  
ContractSize | Float | The contract size of the symbol, for which a position is opened.  
Position | Integer | The ticket (unique identifier) of a trade position in a MetaTrader 5 platform.  
ExternalID | String | The position ticket (unique number) in an external trading system.  
TimeCreate | DateTime | Time of position creation, in seconds that have elapsed since 01.01.1970.  
TimeUpdate | DateTime | Time of the last modification of a position, in seconds that have elapsed since 01.01.1970. The modification time of a position is the time of the last modification of its volume. Virtually, it is the time of the last deal performed by the financial instrument that corresponds to that position.  
TimeCreateMsc | DateTime | Position generation time in the YYYY-MM-DD HH:MM:SS.MS format.  
TimeUpdateMsc | DateTime | Time of a trading position last change in the YYYY-MM-DD HH:MM:SS.MS format. The modification time of a position is the time of the last modification of its volume. Virtually, it is the time of the last deal performed by the financial instrument that corresponds to that position.  
PriceOpen | Float | The weighted average open price of a position. Calculated by the following formula: (price of deal 1 * volume of deal 1 1 + ... + price of deal N * volume of deal N) / (volume of deal 1 + ... + volume of deal N).  
PriceCurrent | Float | The current price of the symbol, for which a trade position has been opened.  
PriceSL | Float | The Stop Loss level of a trade position.  
PriceTP | Float | The Take Profit level of a trade position.  
Volume | Integer | The volume of a trade position. One unit corresponds to 1/10000 lot.  
VolumeExt | Integer | The trade position volume with an extended accuracy. One unit corresponds to 1/100000000 lot.  
Profit | Float | Returns of a trade position in deposit currency.  
Storage | Float | The swap size for a position in deposit currency.  
RateProfit | Float | The exchange rate of the profit currency of a position to the deposit currency of a client group.  
RateMargin | Float | The exchange rate of the margin currency of a position to the client's deposit currency.  
ExpertID | Integer | The ID of the Expert Advisor that has opened the position.  
ExpertPositionID | Integer | Position ID.  
Comment | String | A comment to a position.  
Dealer | Integer | The login of a dealer, who has processed an order, which opened the position.  
ActivationMode | Integer | Position activation type. Passed in a value of the [EnActivation (#enactivation)](mt5-positions/Enumerations.md#enactivation) enumeration.  
ActivationTime | DateTime | Position activation time in the YYYY-MM-DD HH:MM:SS.MS format.  
ActivationPrice | Float | Position activation price.  
ActivationFlags | Integer | Position activation flags. Passed as a value of the [EnTradeActivationFlags (#entradeactivationflags)](mt5-positions/Enumerations.md#entradeactivationflags) enumeration (sum of values of appropriate flags).  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{pos:0,app_id:1,valInt:500,valUInt:500,valDbl:0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.

```

---

<a id='backup-server-sql-export-mt5-prices-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-prices.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_prices

[Previous](mt5-accounts.md) | [Next](mt5-daily.md)

# mt5_prices

Price data of financial instruments is exported to the table. The table contains the following fields:

Name | Type | Description  
Price_ID | Integer | Primary key. Unique symbol ID for more efficient request of the data from the database. Assigned automatically during the export.  
Symbol | String | Symbol name.  
Digits | Integer | The number of decimal places in the price.  
Time | DateTime | The time of quotes coming in the format YYYY-MM-DD HH:MM:SS.  
BidLast | Float | The Bid price.  
BidLow | Float | The lowest bid price for the current day .  
BidHigh | Float | The highest bid price for the current day.  
BidDir | Integer | The direction of change of the bid price relative to its previous state (0 — unchanged, 1 — upwards, 2 — downwards).  
AskLast | Float | The Ask price.  
AskLow | Float | The lowest ask price for the current day.  
AskHigh | Float | The highest ask price for the current day.  
AskDir | Integer | The direction of change of the ask price relative to its previous state (0 — unchanged, 1 — upwards, 2 — downwards).  
LastLast | Float | The price of the last committed transaction.  
LastLow | Float | The lowest price, at which a deal was executed during the current day.  
LastHigh | Float | The highest price, at which a deal was executed during the current day.  
LastDir | Integer | The change direction of the price of the last deal relative to its previous state (0 — unchanged, 1 — upwards, 2 — downwards).

```

---

<a id='backup-server-sql-export-mt5-report-params-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-report-params.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_report_params

[Previous](mt5-reports.md) | [Next](mt5-plugins.md)

# mt5_report_params

Data about [additional report settings (#module)](../../../Platform-Setup/Reports.md#module) is exported to this table. The table contains the following fields:

Name | Type | Description  
ParamID | String | The unique identifier of the parameter.  
Report | String | The name of the report, to which the setting applies.  
Server | Integer | The ID of the trade server, for which the report is configured.  
Type | Integer | Parameter type:

  * 0 — string
  * 1 — integer
  * 2 — floating-point number
  * 3 — time
  * 4 — date
  * 5 — date and time
  * 6 — list of groups
  * 7 — list of symbols

  
Name | String | The name of the parameter.  
Value | String | The value of the parameter.

```

---

<a id='backup-server-sql-export-mt5-reports-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-reports.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_reports

[Previous](mt5-feeder-symbols.md) | [Next](mt5-report-params.md)

# mt5_reports

Data about [report settings](../../../Platform-Setup/Reports.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Name | String | The name of the report configuration.  
Server | Integer | The ID of the trade server, for which the report is configured.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Module | String | The name of the report module.  
Mode | Integer | Report operation mode: 0 — disabled, 1 — enabled.

```

---

<a id='backup-server-sql-export-mt5-routing-conds-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-routing-conds.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_routing_conds

[Previous](mt5-routing-dealers.md) | [Next](mt5-feeders.md)

# mt5_routing_conds

Data about [additional conditions (#condition)](../../../Platform-Setup/Routing/Actions-and-Conditions.md#condition) specified in a routing rule is exported to this table.

Name | Type | Description  
Condition_ID | Integer | The unique identifier of the condition.  
Name | String | The name of the routing rule to which the additional condition applies.  
Condition | Integer | The type of the additional condition for the rule. Passed using the [EnRouteCondition (#enroutecondition)](mt5-routing/Enumerations.md#enroutecondition) enumeration.  
Rule | Integer | A method for comparing a condition with the specified value. Passed using the [EnConditionRule (#enconditionrule)](mt5-routing/Enumerations.md#enconditionrule) enumeration.  
Type | Integer | The type of value of the additional condition for a routing rule. Based on this field, it is possible to determine the field in which the Condition value is contained: ValueInt, ValueUInt, ValueFloat or ValueString. Possible values:

  * 0 — the current parameter does not have values (currently not used)
  * 1 — the value is located in the ValueString field, and its type is string
  * 2 — the value is located in the ValueInt field, and its type is int
  * 3 — the value is located in the ValueUInt field, and its type is uint
  * 4 — the value is located in the ValueFloat field, and its type is float

  
ValueInt | Integer | An int value for the condition.  
ValueUInt | Integer | An uint value for the condition.  
ValueUInt | Integer | An uint value for the condition. Used for volume with extended accuracy.  
ValueFloat | Float | A float value for the condition.  
ValueString | String | A float value for the condition. For example, for the "Symbols" condition, the names of symbol (symbol groups) will be specified in this field.

```

---

<a id='backup-server-sql-export-mt5-routing-dealers-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-routing-dealers.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_routing_dealers

[Previous](mt5-routing/Enumerations.md) | [Next](mt5-routing-conds.md)

# mt5_routing_dealers

Data about [dealers/gateways (#dealers)](../../../Platform-Setup/Routing.md#dealers) to whom trade requests are forwarded for processing in accordance with a routing rule, is exported to this table.

Name | Type | Description  
Login | Integer | The login of a dealer/gateway ID.  
RoutingName | String | The name of the routing rule in which the dealer/gateway is specified.  
Name | String | The name of the dealer/gateway.

```

---

<a id='backup-server-sql-export-mt5-routing-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-routing.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_routing

[Previous](mt5-firewall.md) | [Next](mt5-routing/Enumerations.md)

# mt5_routing

Data about trade request [routing rules](../../../Platform-Setup/Routing.md) is exported to this table. The table contains the following fields:

Name | Type | Description  
Name | String | The name of a routing rule.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has been changed.  
Mode | Integer | The state of a routing rule: 0 — disabled, 1 — enabled.  
Request | Integer | Types of requests for which the rule is applicable. The types are passed using the [EnRouteFlags (#enrouteflags)](mt5-routing/Enumerations.md#enrouteflags) enumeration (as a sum of flags).  
Type | Integer | Types of orders for which the rule is applicable. The types are passed using the [EnTypeFlags (#entypeflags)](mt5-routing/Enumerations.md#entypeflags) enumeration (as a sum of flags).  
Flags | Integer | Currently not used.  
ActionType | Integer | The value type for Action. Based on this field, it is possible to determine the field in which the Action value is contained: ActionValueInt, ActionValueUInt, ActionValueFloat or ActionValueString. Possible values:

  * 0 — the current parameter does not have values (for example, [ACTION_CLEAR_TP (#enrouteaction)](mt5-routing/Enumerations.md#enrouteaction))
  * 1 — the value is located in the ActionValueString field, and its type is string
  * 2 — the value is located in the ActionValueInt field, and its type is int
  * 3 — the value is located in the UInt field, and its type is uint
  * 4 — the value is located in the ActionValueFloat field, and its type is float

  
Action | Integer | The type of action that is applied to a request in accordance with a rule. Passed as a value of the [EnRouteAction (#enrouteaction)](mt5-routing/Enumerations.md#enrouteaction) enumeration.  
ActionValueInt | Integer | An int value for the action applied to the rule. For example, for the rule "pass to online dealers", the 0 value means that the additional option "skip this rule if no dealers online" is disabled.  
ActionValueUInt | Integer | An uint value for the action applied to the rule.  
ActionValueFloat | Fraction | A float value for the action applied to the rule.  
ActionValueString | String | A string value for the action applied to the rule.

```

---

<a id='backup-server-sql-export-mt5-symbols-sessions-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-symbols-sessions.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_symbols_sessions

[Previous](mt5-symbols/Enumerations.md) | [Next](mt5-groups.md)

# mt5_symbols_sessions

Data on symbols' trade and quoting sessions is exported to the table. The table contains the following fields:

Name | Type | Description  
Session_ID | Integer | Primary key. Unique session ID. Assigned automatically during the export.  
Symbol_ID | Integer | Unique [ID of the symbol](mt5-symbols.md), to which the session is applied.  
Type | Integer | Session type: 0 - quoting, 1 - trade.  
Day | Integer | Day of the week from 0 to 6. 0 - Sunday, 6 - Saturday.  
Open | Integer | The opening time of a trading or quoting session of a symbol in minutes elapsed since 00:00. For example, 100 denotes 01:40.  
Close | Integer | The closing time of a trading or quoting session of a symbol in minutes elapsed since 00:00.

```

---

<a id='backup-server-sql-export-mt5-symbols-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-symbols.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_symbols

[Previous](Installation-and-Setup-of-PostgreSQL.md) | [Next](mt5-symbols/Enumerations.md)

# mt5_symbols

[Symbols'](../../../Platform-Setup/Symbols.md) configurations are exported to the table. The table contains the following fields:

Name | Type | Description  
Symbol_ID | Integer | Primary key. Unique symbol ID for more efficient request of the symbol data from the database. Assigned automatically during the export.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Symbol | String | Symbol name.  
Path | String | Path to a symbol.  
ISIN | String | International Securities Identification Number (ISIN) of a symbol.  
Description | String | Symbol description.  
International | String | The international symbol name.  
Category | String | The name of the category or sector to which the symbol belongs.  
Exchange | String | The name of the exchange in which the security is traded.  
CFI | String | Instrument classification in accordance with the ISO 10962 standard.  
Sector | Integer | The economic sector the instrument belongs to. Passed as a value of the [EnSectors (#ensectors)](mt5-symbols/Enumerations.md#ensectors) enumeration.  
Industry | Integer | The industry branch the instrument belongs to. Passed as a value of the [EnIndustries (#enindustries)](mt5-symbols/Enumerations.md#enindustries) enumeration.  
Country | String | The country of the company whose shares are traded on the stock exchange.  
Basis | String | The underlying asset of a derivative financial instrument.  
Source | String | The name of the source symbol whose quotes are used for the current financial instrument.  
Page | String | The address of the web page of a symbol.  
CurrencyBase | String | The base currency of a symbol.  
CurrencyBaseDigits | Integer | The accuracy of conversion into the base currency.  
CurrencyProfit | String | The profit currency for a symbol.  
CurrencyProfitDigits | Integer | The accuracy of conversion into the profit currency.  
CurrencyMargin | String | The symbol margin currency.  
CurrencyMarginDigits | Integer | The accuracy of conversion into the margin currency.  
Color | COLORREF | The color of the symbol in the "Market Watch" window of the terminals.  
ColorBackground | COLORREF | The color of the symbol background in the "Market Watch" window of the terminals.  
Digits | Integer | The number of decimal places in the price of the symbol.  
Point | Float | Point size. Calculated as 1/10^Digits.  
Multiply | Float | The value to multiply the price to, to get the number of points. Calculated as 10^Digits.  
TickFlags | Integer | Options for working with tick data. Passed as a value of the [EnTicksFlags (#entickflags)](mt5-symbols/Enumerations.md#entickflags) enumeration (sum of values of appropriate flags).  
TickBookDepth | Integer | The range of the Depth of Market.  
FilterSoft | Integer | The soft level of price filtering.  
FilterSoftTicks | Integer | The value of the ticks counter for the soft filtering.  
FilterHard | Integer | The hard level of price filtering.  
FilterHardTicks | Integer | The value of the ticks counter for the hard filtering.  
FilterDiscard | Integer | The discard level of price filtering.  
FilterSpreadMax | Integer | The maximum allowed spread value.  
FilterSpreadMin | Integer | The minimum allowed spread.  
SubscriptionsDelay | Integer | The delivery delay for the quotes provided by subscription. Indicated in minutes.  
TradeMode | Integer | The symbol trading mode. Passed in a value of the [EnTradeMode (#entrademode)](mt5-symbols/Enumerations.md#entrademode) enumeration.  
CalcMode | Integer | The mode of margin and profit calculation. Passed in a value of the [EnCalcMode (#encalcmode)](mt5-symbols/Enumerations.md#encalcmode) enumeration.  
ExecMode | Integer | Execution mode of a symbol. Passed in a value of the [EnExecutionMode (#enexecutionmode)](mt5-symbols/Enumerations.md#enexecutionmode) enumeration.  
GTCMode | Integer | Types of orders that can be set for the symbol. Passed as a value of the [EnGTCMode (#engtcmode)](mt5-symbols/Enumerations.md#engtcmode) enumeration (sum of values of appropriate flags).  
FillFlags | Integer | Types of filling allowed for the symbol. Passed as a value of the [EnFillingFlags (#enfillingflags)](mt5-symbols/Enumerations.md#enfillingflags) enumeration (sum of values of appropriate flags).  
ExpirFlags | Integer | Available types of order expiration for a symbol. Passed as a value of the [EnExpirationFlags (#enexpirationflags)](mt5-symbols/Enumerations.md#enexpirationflags) enumeration (sum of values of appropriate flags).  
Spread | Integer | Symbol spread size.  
SpreadBalance | Integer | Symbol spread balance. Spread balance is set a shift from the equal distribution of the spread value between Bid and Ask prices. For example, if the spread is equal to 10 and it is distributed as -5 Bid/+5 Ask, then the spread balance value is 0. The -6 Bid/+4 Ask ratio corresponds to value -1, ratio -4 Bid/+6 Ask corresponds to value 1.  
SpreadDiff | Integer | Symbol spread difference. This parameter returns the base value of the spread, which is actually equal to 0. To work with spread difference of a particular group, the [corresponding parameter of the group](mt5-groups-symbols.md) should be used.  
SpreadDiffBalance | Integer | Spread balance difference. This parameter returns the base value of the balance of spread difference, which is actually equal to 0. To work with the balance of spread difference of a certain group, the [corresponding parameter of the group](mt5-groups-symbols.md) should be used.  
TickValue | Float | The price of one tick of a symbol.  
TickSize | Float | The size of one tick of a symbol.  
ContractSize | Float | The contract size for the symbol.  
StopsLevel | Integer | The price band, within which placing stop orders is not allowed.  
FreezeLevel | Integer | The price band, within which it is not allowed to modify orders and positions.  
QuotesTimeout | Integer | The time to wait for quotes in seconds, after which trading is automatically disabled for the symbol.  
VolumeMin | Integer | The minimum volume of trade operations for a symbol. One unit corresponds to 1/10000 lot.  
VolumeMinExt | Integer | The minimum volume of trade operations for the symbol for the group with extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeMax | Integer | The maximum volume of trade operations for a symbol. One unit corresponds to 1/10000 lot.  
VolumeMaxExt | Integer | The maximum volume of trade operations for the symbol for the group with extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeStep | Integer | The volume change step for trade operations for a symbol. One unit corresponds to 1/10000 lot.  
VolumeStepExt | Integer | The volume change step allowed for trade operations for the symbol, with extended accuracy. One unit corresponds to 1/100000000 lot.  
VolumeLimit | Integer | The maximum allowed aggregate volume of positions and orders for a symbol in one direction. One unit corresponds to 1/10000 lot.  
VolumeLimitExt | Integer | The maximum aggregate volume (with extended accuracy) of positions and orders for the symbol in one direction. One unit corresponds to 1/100000000 lot.  
MarginFlags | Integer | Additional margin checking modes. Passed in a value of the [EnMarginFlags (#enmarginflags)](mt5-symbols/Enumerations.md#enmarginflags) enumeration.  
MarginInitial | Float | The size of the initial margin.  
MarginMaintenance | Float | The size of the maintenance margin.  
MarginInitialBuy | Float | The initial margin rate for market Buy orders.  
MarginInitialSell | Float | The initial margin rate for market Sell orders.  
MarginInitialBuyLimit | Float | The initial margin rate for Buy Limit orders.  
MarginInitialSellLimit | Float | The initial margin rate for Sell Limit orders.  
MarginInitialBuyStop | Float | The initial margin rate for Buy Stop orders.  
MarginInitialSellStop | Float | The initial margin rate for Sell Stop orders.  
MarginInitialBuyStopLimit | Float | The initial margin rate for Buy Stop Limit orders.  
MarginInitialSellStopLimit | Float | The initial margin rate for Sell Stop Limit orders.  
MarginMaintenanceBuy | Float | The maintenance margin rate for market Buy orders.  
MarginMaintenanceSell | Float | The maintenance margin rate for market Sell orders.  
MarginMaintenanceBuyLimit | Float | The maintenance margin rate for Buy Limit orders.  
MarginMaintenanceSellLimit | Float | The maintenance margin rate for Sell Limit orders.  
MarginMaintenanceBuyStop | Float | The maintenance margin rate for Buy Stop orders.  
MarginMaintenanceSellStop | Float | The maintenance margin rate for Sell Stop orders.  
MarginMaintenanceBuyStopLimit | Float | The maintenance margin rate for Buy Stop Limit orders.  
MarginMaintenanceSellStopLimit | Float | The maintenance margin rate for Sell Stop Limit orders.  
MarginHedged | Float | The hedged margin value.  
SwapMode | Integer | The swap calculation mode for a symbol. Passed in a value of the [EnSwapMode (#enswapmode)](mt5-symbols/Enumerations.md#enswapmode) enumeration.  
SwapLong | Float | The swap size for long positions.  
SwapShort | Float | The swap size for short positions.  
SwapYearDay | Integer | The number of days in a year used in calculating swap percent. Passed by the [EnSwapDays (#enswapdays)](mt5-symbols/Enumerations.md#enswapdays) enumeration value.  
SwapFlags | Integer | Additional swap settings. Passed by the [EnSwapFlags (#enswapflags)](mt5-symbols/Enumerations.md#enswapflags) enumeration value.  
SwapRateSunday | Float | Swap multiplier for Sundays.  
SwapRateMonday | Float | Swap multiplier for Mondays.  
SwapRateTuesday | Float | Swap multiplier for Tuesdays.  
SwapRateWednesday | Float | Swap multiplier for Wednesdays.  
SwapRateThursday | Float | Swap multiplier for Thursdays.  
SwapRateFriday | Float | Swap multiplier for Fridays.  
SwapRateSaturday | Float | Swap multiplier for Saturdays.  
TimeStart | Integer | The start date of trading for a symbol. It is considered that there is no time limitation for trading by a symbol if both TimeStart and TimeExpiration are equal to 0.  
TimeExpiration | Integer | The date of trading expiration for a symbol. It is considered that there is no time limitation for trading by a symbol if both TimeStart and TimeExpiration are equal to 0.  
REFlags | Integer | The request execution flags. Passed as a value of the [EnRequestsFlags (#enrequestflags)](mt5-symbols/Enumerations.md#enrequestflags) enumeration (sum of values of appropriate flags).  
RETimeout | Integer | Time in seconds during which the price issued by a dealer in the request execution mode is valid.  
IECheckMode | Integer | Check mode for instant execution. Passed in a value of the [EnInstantMode (#eninstantmode)](mt5-symbols/Enumerations.md#eninstantmode) enumeration.  
IETimeout | Integer | The maximum allowed difference between the time of arrival of the price, at which the client places an order, and the time of the last price.  
IESlipProfit | Integer | The maximum allowed slippage in the profitable direction during instant execution.  
IESlipLosing | Integer | The maximum allowed slippage in the loss direction during instant execution.  
IEVolumeMax | Integer | The maximum volume of a trade operation that can be executed in the instant execution mode. One unit corresponds to 1/10000 lot.  
IEVolumeMaxExt | Integer | The maximum volume (with extended accuracy) of a trade operation that can be executed in the instant execution mode. One unit corresponds to 1/100000000 lot.  
PriceSettle | Float | The clearing price of the previous session.  
PriceLimitMax | Float | The maximum allowed price of the symbol.  
PriceLimitMin | Float | The minimum allowed price of the symbol.  
TradeFlags | Integer | The trade flags of the symbol. Passed in a value of the [EnTradeFlags (#entradeflags)](mt5-symbols/Enumerations.md#entradeflags) enumeration.  
OrderFlags | Integer | The flags of order types that are allowed for the symbol. Passed in a value of the [EnOrderFlags (#enorderflags)](mt5-symbols/Enumerations.md#enorderflags) enumeration (sum of values of appropriate flags).  
MarginRateLiquidity | Float | The liquidity rate of the symbol. It determines the amount of the current value of an asset for the specified financial instrument, which will be taken into account as collateral (accounted for in client's equity).  
MarginRateCurrency | Float | The margin currency rate (rate change radius of the currency, a futures contract is denominated in, relative to the Russian ruble).  
FaceValue | Float | The face value of a bond.  
AccruedInterest | Float | The accrued interest of a bond.  
SpliceType | Integer | The futures contract splicing type.  
SpliceTimeType | Integer | The date of splicing of the futures contracts.  
SpliceTimeDays | Integer | The offset of splicing of the futures contracts.  
OptionMode | Integer | [Option](../../../Platform-Setup/Symbols/Symbol-Settings/Options.md) type and style:

  * 0 means a European call option
  * 1 means a European put option
  * 2 means an American call option
  * 3 means an American put option

  
PriceStrike | Float | The price, at which an option gives the right to buy or sell an asset (the strike price).  
FilterGap | Integer | The difference between the previous and the next quote, starting from which a [gap (#gap)](../../../Platform-Setup/Symbols/Symbol-Settings/Quotes.md#gap) is considered to be formed.  
FilterGapTicks | Integer | The number of ticks for disabling the [gap mode (#gap)](../../../Platform-Setup/Symbols/Symbol-Settings/Quotes.md#gap). If no new gap occurs within the specified number of quotes, the mode is disabled.  
TickChartMode | Integer | The mode of creation of the symbol chart: 0 — using the Bid price, 1 — using the Last price.

```

---

<a id='backup-server-sql-export-mt5-time-weekdays-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-time-weekdays.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_time_weekdays

[Previous](mt5-time.md) | [Next](mt5-gateways.md)

# mt5_time_weekdays

Platform's [working time schedule (#daily-settings)](../../../Platform-Setup/Time.md#daily-settings) by days is exported to this table. The table contains the following fields:

Name | Type | Description  
TimeZone | Integer | The time zone of a server in minutes from GMT. For example: 0 = GMT, -60 = GMT - 1, 60 = GMT + 1. Corresponds to the TimeZone value in the [mt5_time](mt5-time.md) table.  
Day | Integer | The ordinal number of the day of the week. For example, 0 is Sunday, 6 is Saturday.  
00 | Integer | Flag of working time in the period from 00:00 to 00:59. 0 — non-working time, 1 — working time.  
01 | Integer | Flag of working time in the period from 01:00 to 01:59. 0 — non-working time, 1 — working time.  
... | Integer | Further similar fields apply for each hour of the day.  
23 | Integer | Flag of working time in the period from 23:00 to 23:59. 0 — non-working time, 1 — working time.

```

---

<a id='backup-server-sql-export-mt5-time-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-time.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_time

[Previous](mt5-plugin-params.md) | [Next](mt5-time-weekdays.md)

# mt5_time

Platform [trading time settings](../../../Platform-Setup/Time.md) are exported to this table. The table contains the following fields:

Name | Type | Description  
TimeZone | Integer | The time zone of a server in minutes from GMT. For example: 0 = GMT, -60 = GMT - 1, 60 = GMT + 1.  
Timestamp | Integer | A unique value within the table. Used by MetaTrader 5 servers for internal purposes. If the Timestamp of a record has changed, it means that the record has changed.  
TimeServer | String | The address of the current time synchronization server.  
Daylight | Integer | Daylight Saving Time mode: 0 — off, 1 — on.  
DaylightState | Integer | The presence of the daylight saving time in the platform time zone. 0 means no daylight saving time is applied in the platform time zone. Otherwise, any non-zero value is used.

```

---

<a id='backup-server-sql-export-mt5-users-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-users.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Backup Server](../../Backup-Server.md) / [SQL Export](../SQL-Export.md) / mt5_users

[Previous](mt5-documents.md) | [Next](mt5-users/Enumerations.md)

# mt5_users

Data on [account](../../../Platform-Setup/Accounts.md) database is exported to the table. The table contains the following fields:

Name | Type | Description  
Login | Integer | Primary key. The login of a user.  
Timestamp | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
TimestampTrade | Integer | Unique record within the table. It is used for internal purposes of MetaTrader 5 servers. If the timestamp is changed for a record, it means that the record has been changed.  
Group | String | User group.  
CertSerialNumber | Integer | The number of a last used certificate for user authorization.  
Rights | Integer | Flags of the users permissions. Passed using a value of the [EnUserRights (#enusersrights)](mt5-users/Enumerations.md#enusersrights) enumeration (sum of values of appropriate flags).  
Registration | DateTime | Time of a client record generation in the YYYY-MM-DD HH:MM:SS format.  
LastAccess | DateTime | The date of the last connection using an account in the YYYY-MM-DD HH:MM:SS format. This field is not updated in real time, in order to save traffic and reduce the load on the platform. The value is only updated when the user connects to the platform, if more than 24 hours have passed since the previous connection.  
LastPassChange | DateTime | The date of the last password change.  
LastIP | String | The IP address from which the user last connected to the server.  
Name | String | The name of the user. Obsolete field.  
FirstName | String | The first name of the client.  
LastName | String | The last name of the client.  
MiddleName | String | The middle name of the client.  
Company | String | The name of user's company.  
Account | String | The number of a user's account in an external bank.  
Country | String | The user's country of residence.  
Language | Integer | User's language in the format LANGID used in [MS Windows](https://msdn.microsoft.com/en-us/library/windows/desktop/dd318693) (value from Prim.lang.identifier).  
ClientID | Integer | The identifier of the [client](../../../Platform-Setup/Clients.md), to whom the trading account corresponds.  
City | String | The user's city of residence.  
State | String | The user's state (region) of residence.  
ZIPCode | String | The user's zip code.  
Address | String | The address of the user.  
Phone | String | The user's phone number.  
EMail | String | The email address of the user.  
ID | String | The number of a user's identity document.  
Status | String | Client's status.  
Comment | String | A comment to the user.  
Color | COLORREF | The color of the user. This is the color of the user's requests shown when handling the requests via the manager terminal.  
PhonePassword | String | The user's phone password.  
Leverage | Integer | The size of a user's leverage.  
Agent | Integer | Agent account number of the user.  
Balance | Float | The current balance of a user.  
Credit | Float | The current amount of funds credited to the user.  
InterestRate | Float | The amount accrued for the current month calculated based on the annual interest rate.  
CommissionDaily | Float | The amount of commissions charged from the user for a day.  
CommissionMonthly | Float | The total amount of commissions charged from the user for the current month.  
BalancePrevDay | Float | The value of the user's balance as of the end of the previous day.  
BalancePrevMonth | Float | The value of a user's balance as of the end of the previous trading month.  
EquityPrevDay | Float | The user's equity as of the end of the previous day.  
EquityPrevMonth | Float | The value of the user's equity as of the end of the previous trading month.  
TradeAccounts | String | Account numbers in external trading systems and gateway identifiers used for working with that systems. The string format is: gateway_ID=account_number|gateway_ID=account_number...  
MQID | String | MetaQuotes ID of the user.  
LeadCampaign | String | Name of the [marketing campaign (#leadsource)](../../../Platform-Setup/Accounts/Editing-Account.md#leadsource) a client was attracted by.  
LeadSource | String | [Lead source (#leadsource)](../../../Platform-Setup/Accounts/Editing-Account.md#leadsource) (address of the website a client has come from).  
ApiData | String | User data which can be added via MetaTrader 5 API. Sample user data entry: [{pos:0,app_id:1,valInt:500,valUInt:500,valDbl:0.00000000}]. It specifies the user data index, the ID of the application that added it, as well as the data of three types: Int, UInt and double. The string may contain up to 16 such entries.  
LimitOrders | Integer | The maximum number of active (placed) pending orders allowed on the account.  
LimitPositions | Integer | Maximum value of open positions allowed on the account.

```

---

<a id='backup-server-sql-export-mt5-deals-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-deals/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_deals](../mt5-deals.md) / Enumerations

[Previous](../mt5-deals.md) | [Next](../mt5-accounts.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

To pass information about deals the following enumerations are used:

  * [EnDealAction (#endealaction)](Enumerations.md#endealaction)
  * [EnEntryFlags (#enentryflags)](Enumerations.md#enentryflags)
  * [EnDealReason (#endealreason)](Enumerations.md#endealreason)



<a id="endealaction"></a>
## EnDealAction (#endealaction)

Types of actions performed by a deal are enumerated in EnDealAction.

ID number | Value | Description  
DEAL_BUY | 0 | A Buy deal.  
DEAL_SELL | 1 | A Sell deal.  
DEAL_BALANCE | 2 | Balance operation.  
DEAL_CREDIT | 3 | Credit operation.  
DEAL_CHARGE | 4 | Additional charges/withdrawals.  
DEAL_CORRECTION | 5 | Correcting operations.  
DEAL_BONUS | 6 | Bonuses.  
DEAL_COMMISSION | 7 | Commission.  
DEAL_COMMISSION_DAILY | 8 | Daily commission.  
DEAL_COMMISSION_MONTHLY | 9 | Monthly commission.  
DEAL_AGENT_DAILY | 10 | Daily agent commission.  
DEAL_AGENT_MONTHLY | 11 | Daily agent commission.  
DEAL_INTERESTRATE | 12 | Accrual of annual interest.  
DEAL_BUY_CANCELED | 13 | A canceled Buy deal. Using the IMTExecution::TE_DEAL_CANCEL trade execution, the Gateway API can notify the platform about the cancellation of a previously executed deal in the external trading system. In this case the type of the earlier executed Buy trade is replaced with this one. The profit/loss of a trade is cleared. Then the client's position is recalculated and the appropriate profit/loss is added/subtracted as a separate balance operation. Deal cancellation does not change the client's order history. Deal cancellation does not entail changes in client's orders history. A deal of the DEAL_BUY_CANCELED type is not included into the calculation of the financial state of account and is not taken into account in recalculated positions.  
DEAL_SELL_CANCELED | 14 | A canceled Sell deal. Using the IMTExecution::TE_DEAL_CANCEL trade execution, the Gateway API can notify the platform about the cancellation of a previously executed deal in the external trading system. In this case the type of the earlier executed Buy trade is replaced with this one. The profit/loss of a trade is cleared. Then the client's position is recalculated and the appropriate profit/loss is added/subtracted as a separate balance operation. Deal cancellation does not change the client's order history. Deal cancellation does not entail changes in client's orders history. A deal of the DEAL_SELL_CANCELED type is not included into the calculation of the financial state of account and is not taken into account in recalculated positions.  
DEAL_DIVIDEND | 15 | Dividend operations.  
DEAL_DIVIDEND_FRANKED | 16 | Franked (non-taxable) dividend operations (tax is paid by a company, not a client).  
DEAL_TAX | 17 | Charging a tax.  
DEAL_AGENT | 18 | Charging an agent commission. Used in case of an instant commission charge to an agent (every time the agent's client performs a deal).  
DEAL_SO_COMPENSATION | 19 | An operation connected with the [compensation of a negative account (#compensate)](../../../../Platform-Setup/Groups/Group-Settings.md#compensate) after the Stop Out event.  
DEAL_SO_COMPENSATION_CREDIT | 20 | [Withdrawing credit funds (#so-credit)](../../../../Platform-Setup/Groups/Group-Settings.md#so-credit) after a negative balance compensation operation.  
  
<a id="enentryflags"></a>
## EnEntryFlags (#enentryflags)

Types of actions performed by a deal with respect to positions are enumerated in EnEntryFlags.

ID number | Value | Description  
ENTRY_IN | 0 | Entering the market or adding the volume.  
ENTRY_OUT | 1 | Exit from the market or partial closure.  
ENTRY_INOUT | 2 | Reversal.  
ENTRY_OUT_BY | 3 | Close by — a simultaneous closure of two opposite positions of the sane financial instrument. This operation type is only used in the [hedging mode (#hedging)](../../../../Platform-Setup/Groups/Position-Accounting-Systems.md#hedging).  
  
<a id="endealreason"></a>
## EnDealReason (#endealreason)

Types of reasons for order placing are listed in EnDealReason.

ID number | Value | Description  
DEAL_REASON_CLIENT | 0 | Deal performed by a client manually through the client terminal.  
DEAL_REASON_EXPERT | 1 | Deal performed by a client with using an Expert Advisor.  
DEAL_REASON_DEALER | 2 | Deal performed by a dealer through the manager terminal.  
DEAL_REASON_SL | 3 | Deal performed as a result of Stop Loss activation.  
DEAL_REASON_TP | 4 | Deal performed as a result of Take Profit activation.  
DEAL_REASON_SO | 5 | Deal performed when the client reached the Stop-Out level.  
DEAL_REASON_ROLLOVER | 6 | Deal performed when reopening a position for charging swaps.  
DEAL_REASON_EXTERNAL_CLIENT | 7 | Deal performed by a client from an external trading system. For this type of deals the commission is charged as distinct from DEAL_REASON_EXTERNAL_SERVICE.  
DEAL_REASON_VMARGIN | 8 | Deal performed for accruing variation margin.  
DEAL_REASON_GATEWAY | 9 | Deal performed by a MetaTrader 5 gateway that had connected to the trading platform.  
DEAL_REASON_SIGNAL | 10 | Deal performed as a result of copying [a trade signal](https://www.mql5.com/en/signals "Trading signals") according to a subscription in the client terminal.  
DEAL_REASON_SETTLEMENT | 11 | Deal performed to compulsory close a position due to the settlement of a futures contract/option.  
DEAL_REASON_TRANSFER | 12 | Deal performed due to transferring a position at the settlement price to a new symbol with the same underlying asset.  
DEAL_REASON_SYNC | 13 | Deal performed as a result of synchronization of an account's trade state with an external system.  
DEAL_REASON_EXTERNAL_SERVICE | 14 | Deal performed from an external trading system for technical reasons (for example, to correct the trade state of a client). For this type of deals the commission is not charged.  
DEAL_REASON_MIGRATION | 15 | Deal created as a result of importing trade operations from a MetaTrader 4 server.  
DEAL_REASON_MOBILE | 16 | The deal is conducted via the MetaTrader 5 mobile terminal for Android or iPhone.  
DEAL_REASON_WEB | 17 | The deal is conducted via the web terminal.  
DEAL_REASON_SPLIT | 18 | The deal is conducted as a result of a symbol split.  
DEAL_REASON_CORPORATE_ACTION | 19 | The deal is created as a result of a corporate action, such as consolidating or renaming securities, transferring a client to a different account, etc. API applications set this flag for service operations so that the platform does not account for such corporate actions in commission calculations.

```

---

<a id='backup-server-sql-export-mt5-feeders-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-feeders/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_feeders](../mt5-feeders.md) / Enumerations

[Previous](../mt5-feeders.md) | [Next](../mt5-feeder-translates.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

The following enumerations are used for passing information about data feed configurations:

  * [EnFeederFlags (#enfeederflags)](Enumerations.md#enfeederflags)
  * [EnFeedersFieldFlags (#enfeedersfieldflags)](Enumerations.md#enfeedersfieldflags)



<a id="enfeederflags"></a>
## EnFeederFlags (#enfeederflags)

Flags of predefined data feed settings are listed in EnFeederFlags.

Identifier | Value | Description  
FEED_FLAG_QUOTES | 1 | The data feed sends quotes.  
FEED_FLAG_NEWS | 2 | The data feed sends news.  
FEED_FLAG_REMOTE | 8 | The data feed is running on a remote computer.  
  
<a id="enfeedersfieldflags"></a>
## EnFeedersFieldFlags (#enfeedersfieldflags)

Flags of editable fields are listed in EnFeedersFieldFlags.

Identifier | Value | Description  
FEED_FIELD_SERVER | 1 | The "Server" field.  
FEED_FIELD_LOGIN | 2 | The "Login" field.  
FEED_FIELD_PASS | 4  | The "Password" field.  
FEED_FIELD_PARAM | 8 | The "Parameters" field.

```

---

<a id='backup-server-sql-export-mt5-groups-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-groups/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_groups](../mt5-groups.md) / Enumerations

[Previous](../mt5-groups.md) | [Next](../mt5-groups-symbols.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

To pass information about groups the following enumerations are used:

  * [EnPermissionsFlags (#enpermissionsflags)](Enumerations.md#enpermissionsflags)
  * [EnAuthMode (#enauthmode)](Enumerations.md#enauthmode)
  * [EnReportsMode (#enreportsmode)](Enumerations.md#enreportsmode)
  * [EnReportsFlags (#enreportsflags)](Enumerations.md#enreportsflags)
  * [EnNewsMode (#ennewsmode)](Enumerations.md#ennewsmode)
  * [EnMailMode (#enmailmode)](Enumerations.md#enmailmode)
  * [EnHistoryLimit (#enhistorylimit)](Enumerations.md#enhistorylimit)
  * [EnFreeMarginMode (#enfreemarginmode)](Enumerations.md#enfreemarginmode)
  * [EnStopOutMode (#enstopoutmode)](Enumerations.md#enstopoutmode)
  * [EnTradeFlags (#entradeflags)](Enumerations.md#entradeflags)
  * [EnMarginFreeProfitFlags (#enmarginfreeprofitflags)](Enumerations.md#enmarginfreeprofitflags)



<a id="enpermissionsflags"></a>
## EnPermissionsFlags (#enpermissionsflags)

Flags of permissions for groups are listed in EnPermissionsFlags.

ID | Value | Description  
PERMISSION_NONE | 0x00000000 | No permissions. Default value.  
PERMISSION_CERT_CONFIRM | 0x00000001 | Enable confirmation of certificates.  
PERMISSION_ENABLE_CONNECTION | 0x00000002 | Allow client connections.  
PERMISSION_RESET_PASSWORD | 0x00000004 | Force users to change their master password at first login. A user will not be able to take any actions before changing the password.  
PERMISSION_FORCED_OTP_USAGE | 0x00000008 | In some countries, regulators require use of additional account security measures, such as the use of OTP. When this flag is enabled, all clients in this group will need to use one-time passwords to connect. Otherwise, clients can bind their accounts to the generator or use the default authentication method. Before you enable it, please inform your clients about the new OTP option. Be extremely careful when enabling this option for the only one manager group on the trading server. For generating one-time passwords, the mobile terminal MetaTrader 5 for iPhone is used for generating one-time passwords.  
PERMISSION_RISK_WARNING | 0x00000010 | If this flag is enabled, when a client connects in the trading terminal, a warning about the risks associated with operations on the financial markets appears. Trade operations on a client's account are not allowed until the client confirms that he or she has read the warning and is aware of the risks. To confirm, the client should check "I am aware of the risks and I wish to trade high risk investment products". This warning is displayed once per session of the terminal. The next time it will appear after the restart of the terminal.  
PERMISSION_REGULATION_PROTECT | 0x00000020 | Enforce country-specific regulatory restrictions for retail clients. Every country has regulators — state bodies that supervise the activities of financial institutions (including brokers). Each regulator has its own set of requirements applied to trading currencies, securities and other instruments. In most cases, clients of brokerage firms are individuals from different countries. The platform provides the means of meeting the requirements of certain regulators without interfering with the work of traders not covered with these requirements. Restrictions applied to trader accounts depend on the client's country and other conditions set by that country's regulator. For example, the National Securities Market Commission (Comisión Nacional del Mercado de Valores) of Spain compels brokers to warn clients using the leverage of 1:10 or higher about potential risks in a special way. Therefore, if a client's country is Spain and they use a leverage of 1:10 or higher, an additional warning is displayed in the trading dialog Currently, only one regional limitation is used in the platform. The list is to be expanded later.  
PERMISSION_NOTIFY_DEALS | 0x00000040 | Allow accounts to subscribe to [server push notifications  (#push)](../../../../Platform-Setup/Groups/Group-Settings.md#push) about deals.  
PERMISSION_NOTIFY_ORDERS | 0x00000080 | Allow accounts to subscribe to server push notifications about orders.  
PERMISSION_NOTIFY_BALANCES | 0x00000100 | Allow accounts to subscribe to server push notifications about balance operations.  
  
<a id="enauthmode"></a>
## EnAuthMode (#enauthmode)

Types of authorization of clients in the group are listed in EnAuthMode.

ID | Value | Description  
AUTH_STANDARD | 0 | Standard authorization.  
AUTH_RSA1024 | 1 | Extended authorization with 1024-bit encryption.  
AUTH_RSA2048 | 2 | Extended authorization with 2048-bit encryption.  
  
<a id="enreportsmode"></a>
## EnReportsMode (#enreportsmode)

Report generation modes are listed in EnReportsMode.

ID | Value | Description  
REPORTS_DISABLED | 0 | Reports are disabled.  
REPORTS_FULL | 1 | The platform can save the end-of-day and/or end-of-month states of accounts to a special database. The information includes balance, equity, margin, and other details. The database is located on the trade server, in the bases\daily\daily_*.dat file. Data from the file is used in end-of-day and end-of-month trading reports sent to clients, as well as in some manager reports. If the mode is enabled, the platform will save information on accounts from the selected group to the database. This flag enables the generation of both end-of-day and end-of-month data.  
REPORTS_DAY_ONLY | 2 | Enable data generation for reports only at the end of the day.  
REPORTS_MONTH_ONLY | 3 | Enable data generation for reports only at the end of the month.  
  
<a id="enreportsflags"></a>
## EnReportsFlags (#enreportsflags)

Report generation options are listed in IMTConGroup::EnReportsFlags.

ID | Value | Description  
REPORTSFLAGS_NONE | 0 | No additional options enabled.  
REPORTSFLAGS_EMAIL | 1 | Enables sending of generated HTML report files to clients by email. Addresses from [trading accounts (#personal)](../../../../Platform-Setup/Accounts/Editing-Account.md#personal) are used for sending.  
REPORTSFLAGS_SUPPORT | 2 | Enables sending of report copies to a [technical support email address (#support-email)](../../../../Platform-Setup/Groups/Group-Settings.md#support-email).  
REPORTSFLAGS_STATEMENTS | 4 | Enables account state report generation. The HTML report files are created using templates from the \templates\confirmation\ and \templates\statement\ folders on the trade server. The generate reports, the [REPORTS_STANDARD (#enreportsmode)](Enumerations.md#enreportsmode) mode must be enabled.  
  
<a id="ennewsmode"></a>
## EnNewsMode (#ennewsmode)

Modes of news sending are listed in EnNewsMode.

ID | Value | Description  
NEWS_MODE_DISABLED | 0 | News sending is disabled.  
NEWS_MODE_HEADERS | 1 | Only news headers.  
NEWS_MODE_FULL | 2 | Fill package.  
  
<a id="enmailmode"></a>
## EnMailMode (#enmailmode)

Modes of using the internal mail system are listed in EnMailMode.

ID | Value | Description  
MAIL_MODE_DISABLED | 0 | Disable the internal mail system.  
MAIL_MODE_FULL | 1 | Enable the internal mail system.  
  
<a id="enhistorylimit"></a>
## EnHistoryLimit (#enhistorylimit)

The intervals of trading history available to clients in the group are listed in EnHistoryLimit.

ID | Value | Description  
TRADE_HISTORY_ALL | 0 | The entire history.  
TRADE_HISTORY_MONTHS_1 | 1 | One month.  
TRADE_HISTORY_MONTHS_3 | 2 | Three months.  
TRADE_HISTORY_MONTHS_6 | 3 | Six months.  
TRADE_HISTORY_YEAR_1 | 4 | One year.  
TRADE_HISTORY_YEAR_2 | 5 | Two years.  
TRADE_HISTORY_YEAR_3 | 6 | Three years.  
  
<a id="enfreemarginmode"></a>
## EnFreeMarginMode (#enfreemarginmode)

Modes of using the floating profit/loss in the free margin are listed in EnFreeMarginMode.

ID | Value | Description  
FREE_MARGIN_NOT_USE_PL | 0 | Do not use unrealized profit/loss.  
FREE_MARGIN_USE_PL | 1 | Use unrealized profit/loss.  
FREE_MARGIN_PROFIT | 2 | Use unrealized profit.  
FREE_MARGIN_LOSS | 3 | Use unrealized loss.  
  
<a id="enstopoutmode"></a>
## EnStopOutMode (#enstopoutmode)

Modes for checking Margin Call and Stop Out are listed in EnStopOutMode.

ID | Value | Description  
STOPOUT_PERCENT | 0 | The levels of Margin Call and Stop Out in percentage terms.  
STOPOUT_MONEY | 1 | The levels of Margin Call and Stop Out in money terms.  
  
<a id="entradeflags"></a>
## EnTradeFlags (#entradeflags)

Group trade options are enumerated in EnTradeFlags.

ID | Value | Description  
TRADEFLAGS_NONE | 0x00000000 | Options are disabled.  
TRADEFLAGS_SWAPS | 0x00000001 | Allow charging of swaps.  
TRADEFLAGS_TRAILING | 0x00000002 | Enable trailing stop.  
TRADEFLAGS_EXPERTS | 0x00000004 | Enable trading using Expert Advisors.  
TRADEFLAGS_EXPIRATION | 0x00000008 | Enable order expiration.  
TRADEFLAGS_SIGNALS_ALL | 0x00000010 | Allow using the ["Signals"](https://www.mql5.com/en/signals "Signals in MetaTrader") service in the client terminals.  
TRADEFLAGS_SIGNALS_OWN | 0x00000020 | Allow using the [signals](https://www.mql5.com/en/signals "Signals in MetaTrader") from own servers only. If this flag is set, clients in this groups will be able to subscribe only to the signals created on the basis of accounts opened in your brokerage company. Signals created on the basis of other accounts will not be displayed in the client terminals.   
TRADEFLAGS_SO_COMPENSATION | 0x00000040 | Automatically execute on a client's account the special "so compensation" operation, which increases the balance and sets it to zero, if the balance has become negative after a position was closed by Stop Out. For more details please read the [corresponding section (#compensate)](../../../../Platform-Setup/Groups/Group-Settings.md#compensate).  
TRADEFLAGS_SO_FULLY_HEDGED | 0x00000080 | If the flag is enabled, then Stop out will be performed on accounts having open positions, the zero margin (positions are covered) and negative equity. If the option is disabled, orders and positions will not be forcibly closed in above cases. The flag can be only used on [hedging accounts (#hedging)](../../../../Platform-Setup/Groups/Position-Accounting-Systems.md#hedging).  
TRADEFLAGS_FIFO_CLOSE | 0x00000100 | The position closing mode by FIFO rule. If the flag is enabled, then positions for each instrument can only be closed only in the order in which they were opened: the oldest one should be closed first, then the next one, etc. The option is only valid for hedging accounts, in which traders can have multiple positions for the same financial instrument. There are three main methods to close a position; the flag behavior will be different for each of the methods:

  * Closing from the client terminal: the trader closes the position manually, using a trading robot, based on the Signals service subscription, etc. In case of an attempt to close a position, which does not meet the FIFO rule, the trader will receive an appropriate error.
  * Closing upon Stop Loss or Take Profit activation: these orders are processed on the server side, so the position closure is not requested on the trader (terminal) side, but is initiated by the server. If Stop Loss or Take Profit triggers for a position, and this position does not comply with the FIFO rule (there is an older position fro the same symbol), the position will not be closed. An appropriate message will be printed to the log: "position close prohibited by FIFO rule, position #100448219 buy 3.00 EURUSD 1.11544 sl: 1.11537 tp: 1.11549 take profit activation skipped".
  * Closing upon Stop Out triggering: such operations are also processed on the server side. In a normal mode, in which FIFO-based closing is disabled, in case of [Stop Out (#stopout-processing)](../../../../Platform-Setup/Groups/Group-Settings.md#stopout-processing) positions are closed starting with the one having the largest loss. If this option option is enabled, the open time will be additionally checked for losing positions. The server determines losing positions for each symbol, finds the oldest position for each symbol, and then closes the one which has the greatest loss among the found positions.

  
TRADEFLAGS_HEDGE_PROHIBIT | 0x00000200 | Prohibit opening of opposite positions and placing of opposite orders. If this option is enabled, accounts are not allowed to have oppositely directed positions and orders for the same financial instrument. For example, if the account has a Buy position, then the user cannot open a Sell position or place a pending sell order for the same symbol. If such an attempt is made, the user will receive an error. The option is only valid for groups with the [hedging (#hedging)](../../../../Platform-Setup/Groups/Position-Accounting-Systems.md#hedging) position accounting mode.  
TRADEFLAGS_DEAL_COST | 0x00000400 | Calculate deal execution [costs (#deal-cost)](../../../../Platform-Setup/Groups/Group-Settings.md#deal-cost) and display them in client terminals. All NFA regulated brokers should enable this option.  
TRADEFLAGS_SO_COMPENSATION_CREDIT | 0x00000800 | Works as an addition to the TRADEFLAGS_SO_COMPENSATION flag. If enabled, the credit funds on the account will be set to zero after a negative balance compensation operation. [Credit funds (#so-credit)](../../../../Platform-Setup/Groups/Group-Settings.md#so-credit) are withdrawn in a separate balance operation with the "so credit compensation" type.  
  
<a id="enmarginfreeprofitflags"></a>
## EnMarginFreeProfitFlags (#enmarginfreeprofitflags)

Modes of using of the profit/loss fixed during a trade day in the free margin are enumerated in EnMarginFreeProfitFlags.

ID | Value | Description  
FREE_MARGIN_PROFIT_PL | 0 | Include both profit and loss fixed during a day in the free margin.  
FREE_MARGIN_PROFIT_LOSS | 1 | Include onlyInclude only loss fixed during a day in the free margin. The profits of the client during a trading day are accumulated in the [BlockedProfit](../mt5-accounts.md) field of the trade account and are not included in the free margin. At the end of the trading day, the accumulated profits are credited to the balance and the value of IMTAccount::BlockedProfit is reset. fixed during a day in the free margin.  
  
<a id="enmarginmode"></a>
## EnMarginMode (#enmarginmode)

The models of risk management are enumerated in EnMarginMode. The model defines the type of pre-trade control and the position accounting system used.

ID | Value | Description  
MARGIN_MODE_RETAIL | 0 | Used for the OTC market. Margin calculation is based on the type of instrument, as well as group settings. Netting position accounting system is used.  
MARGIN_MODE_EXCHANGE_DISCOUNT | 1 | Used for the exchange market. Margin calculation is based on the discounts specified in symbol settings. Discounts are set by the broker, however they cannot be lower than the exchange set values.  
MARGIN_MODE_RETAIL_HEDGED | 2 | Used for the OTC market. Margin calculation is based on the type of instrument, as well as group settings. Hedging position accounting system is used.  
  
<a id="enmarginflags"></a>
## EnMarginFlags (#enmarginflags)

EnMarginFlags contains the margin calculation flags.

ID | Value | Description  
MARGIN_FLAGS_NONE | 0 | No flags.  
MARGIN_FLAGS_CLEAR_ACC | 1 | The flag is available only in the [FREE_MARGIN_PROFIT_LOSS (#enmarginfreeprofitflags)](Enumerations.md#enmarginfreeprofitflags) mode. If enabled, the profit accumulated by a client will be released (and thus included in the free margin) at the end of trade day. If this flag is disabled, then it will be possible to release the accumulated profit only using an external application (for example, a gateway). The server will not perform this operation.

```

---

<a id='backup-server-sql-export-mt5-orders-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-orders/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_orders](../mt5-orders.md) / Enumerations

[Previous](../mt5-orders.md) | [Next](../mt5-orders-history.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

To pass information about orders the following enumerations are used:

  * [EnOrderType (#enordertype)](Enumerations.md#enordertype)
  * [EnOrderFilling (#enorderfilling)](Enumerations.md#enorderfilling)
  * [EnOrderTime (#enordertime)](Enumerations.md#enordertime)
  * [EnOrderState (#enorderstate)](Enumerations.md#enorderstate)
  * [EnOrderActivation (#enorderactivation)](Enumerations.md#enorderactivation)
  * [EnOrderReason (#enorderreason)](Enumerations.md#enorderreason)
  * [EnTradeActivationFlags (#entradeactivationflags)](Enumerations.md#entradeactivationflags)


  * [EnTradeModifyFlags (#entrademodifyflags)](Enumerations.md#entrademodifyflags)



<a id="enordertype"></a>
## EnOrderType (#enordertype)

Types of trade orders are listed in EnOrderType.

ID number | Value | Description  
OP_BUY | 0 | A Buy order.  
OP_SELL | 1 | A Sell order.  
OP_BUY_LIMIT | 2 | A Buy Limit order.  
OP_SELL_LIMIT | 3 | A Sell Limit order.  
OP_BUY_STOP | 4 | A Buy Stop order.  
OP_SELL_STOP | 5 | A Sell Stop order.  
OP_BUY_STOP_LIMIT | 6 | A Buy Stop Limit .  
OP_SELL_STOP_LIMIT | 7 | A Sell Stop Limit order.  
OP_CLOSE_BY | 8 | A close by order — closing two oppositely directed positions at a single symbol. This type of operations is used only for the hedging position accounting system ([MARGIN_MODE_RETAIL_HEDGED (#enmarginmode)](../mt5-groups/Enumerations.md#enmarginmode)).  
  
<a id="enorderfilling"></a>
## EnOrderFilling (#enorderfilling)

Types of order filling are listed in EnOrderFilling.

ID number | Value | Description  
ORDER_FILL_FOK | 0 | Fill or Kill. The order must be filled completely or canceled. This type of filling is automatically set for the instant and request execution.  
ORDER_FILL_IOC | 1 | Immediate or Cancel. An order can be filled partially and the residual volume is canceled. This type of filling is only available for the stock and market execution.  
ORDER_FILL_RETURN | 2 | Return the remainder to the queue. This mode is intended only for pending orders.  
  
<a id="enordertime"></a>
## EnOrderTime (#enordertime)

Types of order expiration are listed in EnOrderTime.

ID number | Value | Description  
ORDER_TIME_GTC | 0 | Good till Canceled.  
ORDER_TIME_DAY | 1 | Intraday.  
ORDER_TIME_SPECIFIED | 2 | Specified time.  
ORDER_TIME_SPECIFIED_DAY | 3 | Specified day. An order expires at 00:00 of the specified day or the nearest trading time.  
  
<a id="enorderstate"></a>
## EnOrderState (#enorderstate)

Possible staes of orders are listed in EnOrderState.

ID number | Value | Description  
ORDER_STATE_STARTED | 0 | Started.  
ORDER_STATE_PLACED | 1 | Placed.  
ORDER_STATE_CANCELED | 2 | Canceled.  
ORDER_STATE_PARTIAL | 3 | Partially filled.  
ORDER_STATE_FILLED | 4 | Filled.  
ORDER_STATE_REJECTED | 5 | Rejected.  
ORDER_STATE_EXPIRED | 6 | Expired.  
ORDER_STATE_REQUEST_ADD | 7 | The order passed (by the gateway) to be placed. This state is used for notifying that a request for placing the order is being already processed.  
ORDER_STATE_REQUEST_MODIFY | 8 | The order passed (by the gateway) to be modified. This state is used for notifying that a request for modifying the order is being already processed.  
ORDER_STATE_REQUEST_CANCEL | 9 | The order passed (by the gateway) to be deleted. This state is used for notifying that a request for deleting the order is being already processed.  
  
<a id="enorderactivation"></a>
## EnOrderActivation (#enorderactivation)

Types of order activation are listed in EnOrderActivation.

ID number | Value | Description  
ACTIVATION_NONE | 0 | Not activated.  
ACTIVATION_PENDING | 1 | Activation of a pending order.  
ACTIVATION_STOPLIMIT | 2 | Activation of a Stop Limit order.  
ACTIVATION_EXPIRATION | 3 | Cancellation of an order upon expiration.  
ACTIVATION_STOPOUT | 4 | Order is being removed because of a stop out.  
  
<a id="enorderreason"></a>
## EnOrderReason (#enorderreason)

Types of reasons for order placing are listed in EnOrderReason.

ID number | Value | Description  
ORDER_REASON_CLIENT | 0 | Order placed by a client manually through the client terminal.  
ORDER_REASON_EXPERT | 1 | Order placed by a client with using an Expert Advisor.  
ORDER_REASON_DEALER | 2 | Order placed by a dealer through the manager terminal.  
ORDER_REASON_SL | 3 | Order placed as a result of Stop Loss activation.  
ORDER_REASON_TP | 4 | Order placed as a result of Take Profit activation.  
ORDER_REASON_SO | 5 | Order placed when the client reached the Stop-Out level.  
ORDER_REASON_ROLLOVER | 6 | Order placed when reopening a position for charging swaps.  
ORDER_REASON_EXTERNAL_CLIENT | 7 | Order placed by a client from an external trading system.  
ORDER_REASON_VMARGIN | 8 | Order placed for accruing variation margin.  
ORDER_REASON_GATEWAY | 9 | Order placed by a MetaTrader 5 gateway that had connected to the trading platform.  
ORDER_REASON_SIGNAL | 10 | Order placed as a result of copying [a trade signal](https://www.mql5.com/en/signals "Trading signals") according to a subscription in the client terminal.  
ORDER_REASON_SETTLEMENT | 11 | Order placed as a result of performing operations connected with the settlement of a futures contract/option. Not used at the moment.  
ORDER_REASON_TRANSFER | 12 | Order placed due to transferring a position at the settlement price to a new symbol with the same underlying asset. Not used at the moment.  
ORDER_REASON_SYNC | 13 | Order placed as a result of synchronization of an account's trade state with an external system.  
ORDER_REASON_EXTERNAL_SERVICE | 14 | Order placed from an external trading system for technical reasons (for example, to correct the trade state of a client).  
ORDER_REASON_MIGRATION | 15 | Order created as a result of importing trade operations from a MetaTrader 4 server.  
ORDER_REASON_MOBILE | 16 | Order created via the MetaTrader 5 mobile terminal for Android or iPhone.  
ORDER_REASON_WEB | 17 | Order created via the web terminal.  
ORDER_REASON_SPLIT | 18 | Order created as a result of a symbol split.  
ORDER_REASON_CORPORATE_ACTION | 19 | Order created as a result of a corporate action, such as consolidating or renaming securities, transferring a client to a different account, etc. API applications set this flag for service operations so that the platform does not account for such corporate actions in commission calculations.  
  
<a id="entradeactivationflags"></a>
## EnTradeActivationFlags (#entradeactivationflags)

Types of activation flags that can be assigned to orders upon forming a trade execution are listed in EnTradeActivationFlags:

ID number | Value | Description  
ACTIV_FLAGS_NO_LIMIT | 0x01 | Do not handle reaching of the Limit level.  
ACTIV_FLAGS_NO_STOP | 0x02 | Do not handle the reaching of the stop level.  
ACTIV_FLAGS_NO_SLIMIT | 0x04 | Do not handle reaching of the Stop-Limit level.  
ACTIV_FLAGS_NO_SL | 0x08 | Do not handle activation upon Stop Loss.  
ACTIV_FLAGS_NO_TP | 0x10 | Do not handle activation upon Take Profit.  
ACTIV_FLAGS_NO_SO | 0x20 | Do not handle activation upon Stop-Out.  
ACTIV_FLAGS_NO_EXPIRATION | 0x40 | Do not handle order cancellation upon expiration.  
ACTIV_FLAGS_NONE | 0x00 | No flags.  
  
Flags of orders are inherited by [positions](../mt5-positions.md) created as a result of their execution.

<a id="entrademodifyflags"></a>
## EnTradeModifyFlags (#entrademodifyflags)

EnTradeModifyFlags lists the flags assigned to orders when they are changed by an administrator, manager or API:

ID number | Value | Description  
MODIFY_FLAGS_ADMIN | 0x00000001 | Order changed by an administrator.  
MODIFY_FLAGS_MANAGER | 0x00000002 | Open price has been modified by a manager.  
MODIFY_FLAGS_POSITION | 0x00000004 | Flag not used for orders.  
MODIFY_FLAGS_RESTORE | 0x00000008 | Order restored.  
MODIFY_FLAGS_API_ADMIN | 0x00000010 | Order changed via Manager API administrator interface.  
MODIFY_FLAGS_API_MANAGER | 0x00000020 | Order changed via Manager API manager interface.  
MODIFY_FLAGS_API_SERVER | 0x00000040 | Order changed via Server API.  
MODIFY_FLAGS_API_GATEWAY | 0x00000080 | Order changed via Gateway API.  
ACTIV_FLAGS_NONE | 0x00000000 | No flags.

```

---

<a id='backup-server-sql-export-mt5-positions-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-positions/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_positions](../mt5-positions.md) / Enumerations

[Previous](../mt5-positions.md) | [Next](../mt5-deals.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

To pass information about positions the following enumerations are used:

  * [EnPositionAction (#enpositionaction)](Enumerations.md#enpositionaction)
  * [EnActivation (#enactivation)](Enumerations.md#enactivation)
  * [EnTradeActivationFlags (#entradeactivationflags)](Enumerations.md#entradeactivationflags)
  * [EnPositionReason (#enpositionreason)](Enumerations.md#enpositionreason)



<a id="enpositionaction"></a>
## EnPositionAction (#enpositionaction)

Types of positions are listed in EnPositionAction.

ID number | Value | Description  
POSITION_BUY | 0 | Buy.  
POSITION_SELL | 1 | Sell.  
  
<a id="enactivation"></a>
## EnActivation (#enactivation)

Types of position activation are listed in the EnActivation enumeration.

ID number | Value | Description  
ACTIVATION_NONE | 0 | None.  
ACTIVATION_SL | 1 | Stop Loss.  
ACTIVATION_TP | 2 | Take Profit  
ACTIVATION_STOPOUT | 3 | Stop Out.  
  
<a id="entradeactivationflags"></a>
## EnTradeActivationFlags (#entradeactivationflags)

Flags of trade position activation are listed in the EnTradeActivationFlags enumeration:

ID number | Value | Description  
ACTIV_FLAGS_NO_LIMIT | 0x01 | Do not handle reaching of the Limit level.  
ACTIV_FLAGS_NO_STOP | 0x02 | Do not handle the reaching of the stop level.  
ACTIV_FLAGS_NO_SLIMIT | 0x04 | Do not handle reaching of the Stop-Limit level.  
ACTIV_FLAGS_NO_SL | 0x08 | Do not handle activation upon Stop Loss.  
ACTIV_FLAGS_NO_TP | 0x10 | Do not handle activation upon Take Profit.  
ACTIV_FLAGS_NO_SO | 0x20 | Do not handle activation upon Stop-Out.  
ACTIV_FLAGS_NO_EXPIRATION | 0x40 | Do not handle order cancellation upon expiration.  
ACTIV_FLAGS_NONE | 0x00 | No flags.  
  
Activation flags are inherited from the [orders](../mt5-orders.md), as a result of which the position is created.

<a id="enpositionreason"></a>
## EnPositionReason (#enpositionreason)

Reasons for position opening are enumerated in EnPositionReason:

ID number | Value | Description  
POSITION_REASON_CLIENT | 0 | Position opened manually by a client from the client terminal.  
POSITION_REASON_EXPERT | 1 | Position opened by a client using an Expert Advisor.  
POSITION_REASON_DEALER | 2 | Position opened by a dealer through the manager terminal.  
POSITION_REASON_SL | 3 | Not used for positions.  
POSITION_REASON_TP | 4  | Not used for positions.  
POSITION_REASON_SO | 5 | Not used for positions.  
POSITION_REASON_ROLLOVER | 6 | Position reopened to charge swaps.  
POSITION_REASON_EXTERNAL_CLIENT | 7 | Position opened from an external trading system.  
POSITION_REASON_VMARGIN | 8 | Not used for positions.  
POSITION_REASON_GATEWAY | 9 | Position opened by a MetaTrader 5 gateway connected to the platform.  
POSITION_REASON_SIGNAL | 10 | Position opened as a result of copying a [trading signal](https://www.mql5.com/en/signals "Trading Signals") according to the subscription in the client terminal.  
POSITION_REASON_SETTLEMENT | 11 | Position opened as a result of operations associated with a futures/option delivery date. It is currently not used.  
POSITION_REASON_TRANSFER | 12 | Position opened as a result of transferring a position with a calculated price to a new symbol with the same underlying asset.  
POSITION_REASON_SYNC | 13 | Position opened while synchronizing a trading account state with an external system.  
POSITION_REASON_EXTERNAL_SERVICE | 14 | Position opened in the external trading system for service purposes (e.g. to correct a trading state).  
POSITION_REASON_MIGRATION | 15 | Position opened as a result of import of clients' trading operations from the MetaTrader 4 server.  
POSITION_REASON_MOBILE | 16 | Position opened via the MetaTrader 5 mobile terminal for Android or iPhone.  
POSITION_REASON_WEB | 17 | Position opened via the web terminal.  
POSITION_REASON_SPLIT | 18 | Position opened as a result of a symbol split.  
POSITION_REASON_CORPORATE_ACTION | 19 | Position created as a result of a corporate action, such as consolidating or renaming securities, transferring a client to a different account, etc. API applications set this flag for service operations so that the platform does not account for such corporate actions in commission calculations.

```

---

<a id='backup-server-sql-export-mt5-routing-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-routing/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_routing](../mt5-routing.md) / Enumerations

[Previous](../mt5-routing.md) | [Next](../mt5-routing-dealers.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

The following enumerations are used for passing information about trade routing rules:

  * [EnRouteFlags (#enrouteflags)](Enumerations.md#enrouteflags)
  * [EnTypeFlags (#entypeflags)](Enumerations.md#entypeflags)
  * [EnRouteAction (#enrouteaction)](Enumerations.md#enrouteaction)
  * [EnRouteCondition (#enroutecondition)](Enumerations.md#enroutecondition)
  * [EnConditionRule (#enconditionrule)](Enumerations.md#enconditionrule)



<a id="enrouteflags"></a>
## EnRouteFlags (#enrouteflags)

Conditions for applying a rule based on the request type are enumerate in EnRouteFlags.

ID | Value | Description  
REQUEST_NONE | 0x00000000 | Conditions by the request type are not specified.  
REQUEST_PRICE | 0x00000001 | Price request (for request execution).  
REQUEST_REQUEST | 0x00000002 | Confirmation of order execution ar a dealer's type in the request execution mode (with the order confirmation option enabled).  
REQUEST_INSTANT | 0x00000004 | Placing an order in the instant execution mode.  
REQUEST_MARKET | 0x00000008 | Placing an order in the market execution mode.  
REQUEST_EXCHANGE | 0x00000010 | Placing an order in the exchange execution mode.  
REQUEST_PENDING | 0x00000020 | Placing a pending order.  
REQUEST_SLTP | 0x00000040 | Modification of Stop Loss and Take Profit of a position.  
REQUEST_MODIFY | 0x00000080 | Modification of a pending order.  
REQUEST_REMOVE | 0x00000100 | Deleting a pending order.  
REQUEST_ACTIVATE | 0x00000200 | Activation (triggering) of a pending order.  
REQUEST_STOPLIMIT | 0x00000400 | Activation of a Stop Limit order.  
REQUEST_SL | 0x00000800 | Triggering of a Stop Loss order.  
REQUEST_TP | 0x00001000 | Triggering of a Take Profit order.  
REQUEST_STOPOUT_ORDER | 0x00002000 | A request to delete a pending order in case of reaching the stop-out level (if margin requirements are set for pending orders)  
REQUEST_STOPOUT_POSITION | 0x00004000 | A request to close a position when reaching stop-out.  
REQUEST_EXPIRATION | 0x00008000 | Cancellation of an order upon expiration.  
REQUEST_DEALER_POS_EXECUTE | 0x00010000 | Position opening and closing by a dealer.  
REQUEST_DEALER_ORD_PENDING | 0x00020000 | Placing of a pending order by a dealer.  
REQUEST_DEALER_POS_MODIFY | 0x00040000 | Position modification by a dealer.  
REQUEST_DEALER_ORD_MODIFY | 0x00080000 | Order modification by a dealer.  
REQUEST_DEALER_ORD_REMOVE | 0x00100000 | Order deletion by a dealer.  
REQUEST_DEALER_ORD_ACTIVATE | 0x00200000 | Order activation by a dealer.  
REQUEST_DEALER_ORD_SLIMIT | 0x00400000 | Activation of a Stop Limit order by a dealer. After this action is performed, the order turns into a limit order.  
REQUEST_DEALER_CLOSE_BY | 0x00800000 | Close By. An operation of closing two oppositely directed positions at a single symbol performed by a dealer.  
REQUEST_CLOSE_BY | 0x01000000 | Close By. An operation of closing two oppositely directed positions at a single symbol performed by a client.  
  
<a id="entypeflags"></a>
## EnTypeFlags (#entypeflags)

Conditions for applying a rule based on the order type are enumerate in EnTypeFlags.

ID | Value | Description  
TYPE_NONE | 0x0000 | No conditions by the order type.  
TYPE_BUY | 0x0001 | A Buy order.  
TYPE_SELL | 0x0002 | A Sell order.  
TYPE_BUY_LIMIT | 0x0004 | A limit Buy order.  
TYPE_SELL_LIMIT | 0x0008 | A limit Sell order.  
TYPE_BUY_STOP | 0x0010 | A stop Buy order.  
TYPE_SELL_STOP | 0x0020 | A stop Sell order.  
TYPE_BUY_STOP_LIMIT | 0x0040 | A limit Buy Stop order.  
TYPE_SELL_STOP_LIMIT | 0x0080 | A limit Sell Stop order.  
  
<a id="enrouteaction"></a>
## EnRouteAction (#enrouteaction)

Types of actions that are applied to requests are listed in EnRouteAction.

ID | Value | Description  
ACTION_DELAY_TIME | 0 | Delay request execution by the specified number of milliseconds. After applying this action to a request, its execution continues in accordance with the created rules located below in the list. The delay is indicated in a separate parameter.  
ACTION_DELAY_TICK | 1 | Delay request execution by the specified number of ticks. After applying this action to a request, its execution continues in accordance with the created rules located below in the list. The delay is indicated in a separate parameter.  
ACTION_CLEAR_TP | 2 | Clear the Take Profit level set in the order.  
ACTION_CLEAR_SL | 3 | Clear the Stop Loss level set in the order.  
ACTION_CLEAR_SLTP | 4  | Clear the Stop Loss and Take Profit levels set in the order.  
ACTION_DEALER | 1001 | Enqueue the request to be processed by the specified dealer. The flag of action omission in case there are no dealers online, is specified by an additional parameter.  
ACTION_DEALER_ONLINE | 1002 | Pass the request to dealers that are currently online. The flag of action omission in case there are no dealers online, is specified by an additional parameter.  
ACTION_REJECT | 1003 | Reject a request.  
ACTION_REQUOTE | 1004 | Send current market prices in response to the request.  
ACTION_CONFIRM_CLIENT | 1005 | Confirm the execution of an order at a price requested in it.  
ACTION_CONFIRM_MARKET | 1006 | Confirm the execution of an order at the current market price.  
ACTION_CANCEL_ORDER | 1007 | Cancel a pending order during its activation or modification. For example, if a pending order has triggered, but the client has already reached the maximum position volume and a new position cannot be opened, the routing rule will remove this order. Otherwise, the order would have continued to trigger on each new tick. When removing an order by this rule, "deleted [by dealer]" is added to the order comment. An entry about the routing rule that canceled the order is also added to the server journal. The server returns error code MT_RET_REQUEST_REJECT_CANCEL. The action can only be applied during pending order activation or modification (including modification buy a dealer). The rule does not affect other trade requests.  
  
<a id="enroutecondition"></a>
## EnRouteCondition (#enroutecondition)

Additional conditions for activation of a routing rule are listed in IMTConCondition::EnRouteCondition.

ID | Value | Description  
CONDITION_DATETIME | 0 | Using this parameter you can compare date and time of a request with that specified in the "Value" field.  
CONDITION_SYMBOL | 1 | This parameter is used for specifying a symbol or a group of symbols requests for which will be subject to the routing rule.  
CONDITION_VOLUME | 2 | Deal volume requested in an order (in lots). This parameter is used for configuring a rule depending on the request volume, e.g. automatic processing of requests less than 1 lot.  
CONDITION_MARKET_DEVIATION | 3 | This condition is applicable only with the instant execution mode. It takes into account the difference between the price of a client's request and the current market price. For Buy trades the deviation is calculated as ("Current Ask price" - "Client's request price"), for Sell trades it is equal to ("Client's request price" - "Current Bid price"). For example, if a client wants to buy at 1.2000, and the current Ask is 1.2008, then the deviation is equal to 1.2008 - 1.2000 = 8 points.  
CONDITION_TIME | 4  | This parameter can be used for comparing the time or a request arrival (in minutes since 00:00) with the value specified in the "Value" field.  
CONDITION_WEEKDAY | 5 | This parameter allows to route requests depending on a day of the week.  
CONDITION_COMMENT | 6 | This parameter allows to compare a request comment with a specified one. If "=" condition is specified, exact match of a comment is checked. If ">" or ">=" conditions are set, a specified substring is searched in a comment string. If "<" or "<=" conditions are set, comment substring is searched in a specified string.  
CONDITION_EXPERT | 7 | This parameter allows to route requests placed by MQL5 programs.  
CONDITION_SIGNAL | 8 | All operations copied by the client terminal in accordance with the subscription to a [trading signal](https://www.mql5.com/en/signals "Trading Signals") are marked with a special flag. This parameter allows routing trade requests created by trade signals. If this condition is enabled, the rule will trigger for all signal operations.  
CONDITION_DEALER_LOGIN | 9 | This parameter allows applying the routing rules depending on a dealer (or gateway) identifier specified in an order or position. The dealer identifier is specified in an order after it has been confirmed (processed) by the dealer/gateway. Due to it, this rule can be applied only when modifying/deleting an order, and not for newly created orders as they do not have a dealer identifier.. For positions, the dealer identifier is specified according to the dealer identifier of the order, whose execution resulted in the position opening.  
This parameter can be used when processing trade operations for a symbol through several gateways simultaneously. An order or position created through a specific gateway must be further processed through the same gateway.  
CONDITION_SOURCE_LOGIN | 10 | The parameter allows routing requests by a login of a dealer who set a request on a client's behalf.  
CONDITION_MARKET_DEVIATION_SPR | 11 | This condition works when executing orders in the Instant or Market modes, as well as when pending orders and Stop Loss/Take Profit orders are triggered. It takes into account the difference between the price of a client's request and the current market price. During a market execution, when a client does not set a price in the order, the difference between the market price during the request and the current market price is taken into account. The deviation is set in spreads. For floating-spread symbols, the current spread valid during the request check is used. For fixed-spread symbols, a spread value from the symbol settings is used. For Buy trades the deviation is calculated as ("Current Ask price" - "Client's request price"), for Sell trades it is equal to ("Client's request price" - "Current Bid price"). For example, if a client wants to buy at 1.2000, and the current Ask is 1.2008, then the deviation is equal to 1.2008 - 1.2000 = 8 points. The current spread is divided by this value and the result is compared with the value in the rule. When setting the condition, keep in mind that if the deviation is positive, opening at the request price is performed in the client's favor, if the deviation is negative, opening is performed against the client. Another example: if we set < -1, the condition corresponds to the buy requests where a request price exceeds the current price by more than 1 spread.  
CONDITION_GAP | 12 | This parameter allows processing trade requests in a special way under the market conditions that differ from normal ones. For example, after a gap, client requests can be rejected or requoted during a certain number of subsequent ticks. The gap mode is defined separately for each symbol according to its settings. The parameter may take two values — true or false (enabled/disabled). If the gap mode is active when checking a request according to the selected symbol routing rule, actions set in this rule are applied to it. The gap mode is checked by an instrument's Bid and Ask prices. If a gap is detected at least on one of the prices, the rule is triggered.  
CONDITION_LOGIN | 1000 | The number of a client's account. This parameter allows creating individual rules for accounts.  
CONDITION_GROUP | 1001 | The group to which the client's account is included. This parameter is used for configuring rules for separate account groups.  
CONDITION_COUNTRY | 1002 | In this parameter a client's country can be specified. The specified rule will be applied to all clients living in this country.  
CONDITION_CITY | 1003 | Use this parameter to apply the rule to all clients living in a specified city.  
CONDITION_COLOR | 1004 | Use this parameter to apply the rule for clients that are marked with the specified color.  
CONDITION_LEVERAGE | 1005 | Use this parameter to apply the rule for clients with the specified leverage.  
CONDITION_COMMENT_CLIENT | 1006 | Use this parameter to apply the rule for clients with the specified comment.  
CONDITION_MARGIN | 2000 | Use this parameter to set up rule application depending on the margin volume that is currently reserved (in the deposit currency).  
CONDITION_MARGIN_LEVEL | 2001 | This parameter allows using rules depending on the current margin level (in percents).  
CONDITION_MARGIN_FREE | 2002 | This parameter allows using rules depending on the current amount of free margin (in the deposit currency).  
CONDITION_EQUITY | 2003 | This parameter allows using rules depending on the current equity on a client's account (in the deposit currency).  
CONDITION_BALANCE | 2004 | This parameter allows using rules depending on the current balance of a client (in the deposit currency).  
CONDITION_PROFIT | 2005 | This parameter allows using rules depending on the current floating profit of a client.  
CONDITION_DAILY_DEALS | 3000 | This parameter allows using rules depending on the number of deals of a client for the current and previous days (including weekends and holidays).  
CONDITION_DAILY_DEALS_PERIOD | 3001 | The frequency of deals for a day. Calculated on the basis of the last 8 deals (the average time between deals).  
CONDITION_DAILY_PROFIT | 3002 | The profit of the client, whose request is being handled, for the current and previous days (including weekends and holidays).  
CONDITION_POSITION_VOLUME | 4000 | The current volume of a position for the symbol, for which a request has arrived.  
CONDITION_POSITION_PROFIT | 4001 | The current profit of a position for the symbol, for which a request has arrived.  
CONDITION_POSITION_AGE | 4002 | Using this parameter you can specify time in seconds elapsed since position opening for the symbol a request for which is currently being handled. This parameter allows to track positions based on the time they have been held.  
CONDITION_POSITION_MODIFY_TIME | 4003 | Using this parameter you can specify time in seconds elapsed since the last modification of a position for the symbol a request for which is currently being handled. Position modification means increase of its volume, partial closure, and modification of Stop Loss and Take Profit levels. This parameter allows to prevent evasion of the previous rule through manipulating one position, increasing or reducing its volume.  
CONDITION_POSITION_AVERAGE_TIME | 4004 | This parameter allows to track positions based on the time the average age of the position for the symbol for which a request is being handled. The average position age is calculated as follows: Current time — ((Open time + Modification time)/2).  
CONDITION_POSITION_TOTAL | 4005 | This parameter allows tracking the total number of a client's open positions on all symbols. For example, you can set the platform to reject trade requests to open new positions, if the client has reached the specified limit.  
CONDITION_POSITION_TOTAL_SYMBOL | 4006 | The parameter allows tracking the number of positions on the symbol that is specified in the current trade request. For example, if a client has placed an order on EURUSD, this condition will check the current number of the client's open positions on EURUSD.  
CONDITION_ORDER_TOTAL | 4007 | This parameter allows tracking the total number of a client's orders on all symbols. All orders are taken into account, including pending and history orders. Each opening and closing of a position (including partial closure), as well as placing of a pending order increases this counter.  
CONDITION_ORDER_TOTAL_SYMBOL | 4008 | The parameter allows tracking the number of orders on the symbol that is specified in the current trade request. For example, if a client has placed an order on EURUSD, this condition will check the current number of the client's orders (both active and history) on EURUSD.  
CONDITION_POSITION_SL_TOUCHED | 4009 | The condition is triggered when the market price touches the stop loss of a position (while the stop loss may not be activated yet). Possible values — true or false.  
CONDITION_POSITION_TP_TOUCHED | 4010 | The condition is triggered when the market price touches the take profit of a position (while the take profit may not be activated yet). Possible values — true or false.  
CONDITION_ORDER_SL_TOUCHED | 4011 | The condition is triggered when the market price touches the stop loss of a pending order. Possible values — true or false. In combination with the REQUEST_ACTIVATE condition, it allows you to track the simultaneous breakthrough of a pending order (trigger) and its stop loss level. This may occur during a release of important news or after a weekend when a large price gap is formed.  
CONDITION_ORDER_TP_TOUCHED | 4012 | The condition is triggered when the market price touches the stop loss of a pending order. Possible values — true or false. In combination with the REQUEST_ACTIVATE condition, it allows you to track the simultaneous breakthrough of a pending order (trigger) and its take profit level. This may occur during a release of important news or after a weekend when a large price gap is formed.  
  
<a id="enconditionrule"></a>
## EnConditionRule (#enconditionrule)

Types of parameter and value comparison are enumerated in IMTConCondition::EnConditionRule.

ID | Value | Description  
RULE_EQ | 0 | Condition of equality.  
RULE_NOT_EQ | 1 | Condition of inequality.  
RULE_GREATER | 2 | Condition of "greater than".  
RULE_NOT_LESS | 3 | Condition of "not less than".  
RULE_LESS | 4  | Condition of "less than".  
RULE_NOT_GREATER | 5 | Condition of "not greater than".

```

---

<a id='backup-server-sql-export-mt5-symbols-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-symbols/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_symbols](../mt5-symbols.md) / Enumerations

[Previous](../mt5-symbols.md) | [Next](../mt5-symbols-sessions.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

To pass information about symbols the following enumerations are used:

  * [EnFillingFlags (#enfillingflags)](Enumerations.md#enfillingflags)
  * [EnExpirationFlags (#enexpirationflags)](Enumerations.md#enexpirationflags)
  * [EnTradeMode (#entrademode)](Enumerations.md#entrademode)
  * [EnExecutionMode (#enexecutionmode)](Enumerations.md#enexecutionmode)
  * [EnCalcMode (#encalcmode)](Enumerations.md#encalcmode)
  * [EnGTCMode (#engtcmode)](Enumerations.md#engtcmode)
  * [EnTickFlags (#entickflags)](Enumerations.md#entickflags)
  * [EnMarginFlags (#enmarginflags)](Enumerations.md#enmarginflags)
  * [EnSwapMode (#enswapmode)](Enumerations.md#enswapmode)
  * [EnSwapDays (#enswapdays)](Enumerations.md#enswapdays)
  * [EnSwapFlags (#enswapflags)](Enumerations.md#enswapflags)
  * [EnInstantMode (#eninstantmode)](Enumerations.md#eninstantmode)
  * [EnRequestFlags (#enrequestflags)](Enumerations.md#enrequestflags)
  * [EnTradeFlags (#entradeflags)](Enumerations.md#entradeflags)
  * [EnOrderFlags (#enorderflags)](Enumerations.md#enorderflags)
  * [EnMarginTypes (#enmargintypes)](Enumerations.md#enmargintypes)
  * [EnSpliceType (#ensplicetype)](Enumerations.md#ensplicetype)
  * [EnSpliceTimeType (#ensplicetimetype)](Enumerations.md#ensplicetimetype)
  * [EnSectors (#ensectors)](Enumerations.md#ensectors)
  * [EnIndustries (#enindustries)](Enumerations.md#enindustries)



<a id="enfillingflags"></a>
## EnFillingFlags (#enfillingflags)

The order filling methods allowed for a symbol are enumerated in EnFillingFlags.

ID | Value | Description  
FILL_FLAGS_NONE | 0 | All filling methods are disabled.  
FILL_FLAGS_FOK | 1 | The "Fill or Kill" mode. The order must be filled completely or canceled. This type of filling is automatically set for the instant and request execution.  
FILL_FLAGS_IOC | 2 | Immediate or Cancel. An order can be filled partially and the residual volume is canceled. This type of filling is only available for the stock and market execution.  
  
<a id="enexpirationflags"></a>
## EnExpirationFlags (#enexpirationflags)

Types of orders allowed for the symbol are enumerated in EnExpirationFlags.

ID | Value | Description  
TIME_FLAGS_NONE | 0 | All expiration types are disabled.  
TIME_FLAGS_GTC | 1 | Orders are good till canceled.  
TIME_FLAGS_DAY | 2 | Orders are effective only during the current trading day.  
TIME_FLAGS_SPECIFIED | 4 | Orders are effective till the date specified by the trader.  
TIME_FLAGS_SPECIFIED_DAY | 8 | Orders that expire at the specified day. An order expires at 00:00 of the specified day or the nearOrders with expiration at a specified day. An order expires at 00:00 of a specified day or at a nearest trade time.est trading time.  
  
<a id="entrademode"></a>
## EnTradeMode (#entrademode)

Symbol trading modes are enumerated in EnTradeMode.

ID | Value | Description  
TRADE_DISABLED | 0 | Trade is disabled.  
TRADE_LONGONLY | 1 | Only long positions are allowed.  
TRADE_SHORTONLY | 2 | Only short positions are allowed.  
TRADE_CLOSEONLY | 3 | Only closure is allowed.  
TRADE_FULL | 4 | Full trading access.  
  
<a id="enexecutionmode"></a>
## EnExecutionMode (#enexecutionmode)

Execution types are enumerated in EnExecutionMode.

ID | Value | Description  
EXECUTION_REQUEST | 0 | Request execution mode.  
EXECUTION_INSTANT | 1 | Instant execution mode.  
EXECUTION_MARKET | 2 | Market execution mode.  
EXECUTION_EXCHANGE | 3 | Exchange execution mode.  
  
<a id="encalcmode"></a>
## EnCalcMode (#encalcmode)

Types of profit and margin calculation for a symbol are enumerated in EnCalcMode.

ID | Value | Description  
TRADE_MODE_FOREX | 0 | The Forex calculation mode.  
TRADE_MODE_FUTURES | 1 | The Futures calculation mode.  
TRADE_MODE_CFD | 2 | The CFD calculation mode.  
TRADE_MODE_CFDINDEX | 3 | The CFD Index calculation mode.  
TRADE_MODE_CFDLEVERAGE | 4 | The CFD Leverage calculation mode.  
TRADE_MODE_FOREX_NO_LEVERAGE | 5 | The Forex No Leverage calculation mode.  
TRADE_MODE_EXCH_STOCKS | 32 | The Exchange Stocks calculation mode.  
TRADE_MODE_EXCH_FUTURES | 33 | The Exchange Futures calculation mode.  
TRADE_MODE_EXCH_FORTS | 34 | The Exchange FORTS calculation mode for Derivatives Market of the Moscow Exchange.  
TRADE_MODE_EXCH_OPTIONS | 35 | The Exchange Options calculation mode.  
TRADE_MODE_EXCH_OPTIONS_MARGIN | 36 | The Exchange Margin Options calculation mode.  
TRADE_MODE_EXCH_BONDS | 37 | The Exchange Bonds calculation mode.  
TRADE_MODE_SERV_COLLATERAL | 64 | Non-tradable instruments of this type are used as client's assets to provide the required margin for open positions of other instruments. For these instruments the margin and profit are not calculated.  
  
<a id="engtcmode"></a>
## EnGTCMode (#engtcmode)

Types of order expiration are enumerated in EnGTCMode.

ID | Value | Description  
ORDERS_GTC | 0 | "Good till canceled" mode. As a trade day changes, pending orders are preserved.  
ORDERS_DAILY | 1 | "Good till today including SL/TP" mode. Orders are effective only within one trading day. As soon as it is over, all Stop Loss and Take Profit levels, as well all pending orders are deleted.  
ORDERS_DAILY_NO_STOPS | 2 | "Good till today excluding SL/TP" mode. As a trading day changes, only pending orders are deleted, while Stop Loss and Take Profit levels are preserved.  
  
<a id="entickflags"></a>
## EnTickFlags (#entickflags)

Options of working with the symbol's tick data are enumerated in EnTickFlags.

ID | Value | Description  
TICK_REALTIME | 1 | Allow real-time quotes from data feeds.  
TICK_COLLECTRAW | 2 | Enable keeping of raw prices.  
TICK_FEED_STATS | 4 | Receive market statistics (Ask High, Bid Low, etc.) directly from data feeds without calculation on the history server. If this flag is not set, the statistical information is calculated by the history server. This flag can only be set together with TICK_REALTIME.  
TICK_NONE | 0 | Beginning of enumeration. Corresponds to the absence of rights.  
  
<a id="enmarginflags"></a>
## EnMarginFlags (#enmarginflags)

The additional margin checks are enumerated in EnMarginFlags.

ID | Value | Description  
MARGIN_FLAGS_NONE | 0 | The standard mode of margin checking. The margin is checked when any order is placed and when a pending orders triggers.  
MARGIN_FLAGS_CHECK_PROCESS | 1 | If this flags is enabled, another check of margin is added to those described above: the margin is checked before executing an order after it is confirmed (checked) by the server (at automated execution), by a dealer or by a gateway.  
MARGIN_FLAGS_CHECK_SLTP | 2 | This flag enables an additional check of margin before a position is closed by stop loss or take profit. If the position close results in reducing the margin to a level insufficient to maintain open positions and orders, the stop loss/take profit will not trigger, the position will stay open. This check must be enabled in case the trade operations are transmitted to an external system (exchange).  
MARGIN_FLAGS_HEDGE_LARGE_LEG | 4 | If the flag is enabled, the margin for hedged positions is calculated using larger leg (the total volume of users positions and orders opened in the same direction).  
  
<a id="enswapmode"></a>
## EnSwapMode (#enswapmode)

Types of swap calculation are enumerated in EnSwapMode. The swap size is specified using the [SwapLong](../mt5-symbols.md) and [SwapShort](../mt5-symbols.md) parameters.

ID | Value | Description  
SWAP_DISABLED | 0 | Swap charging is disabled.  
SWAP_BY_POINTS | 1 | Swap charging in points of a symbol price.  
SWAP_BY_SYMBOL_CURRENCY | 2 | Swap charging in the base currency of a symbol.  
SWAP_BY_MARGIN_CURRENCY | 3 | Swap charging in the margin currency of a symbol.  
SWAP_BY_GROUP_CURRENCY | 4 | Swap charging in the group (deposit) currency.  
SWAP_BY_INTEREST_CURRENT | 5 | Swap charging as a per cent from the price of a symbol at calculation of swap.  
SWAP_BY_INTEREST_OPEN | 6 | Swap charging as a per cent from the open price of a position by a symbol.  
SWAP_REOPEN_BY_CLOSE_PRICE | 7 | Swap charging by reopening position. At the end of a trading day position is closed. Next day it is reopened by the close price +/- number of points specified using the [SwapLong](../mt5-symbols.md) and [SwapShort](../mt5-symbols.md) parameters.  
SWAP_REOPEN_BY_BID | 8 | Swap charging by reopening position. At the end of a trading day position is closed. Next day it is reopened by the current Bid price +/- number of points specified using the [SwapLong](../mt5-symbols.md) and [SwapShort](../mt5-symbols.md) parameters.  
SWAP_BY_PROFIT_CURRENCY | 9 | Swap charging in the profit currency of a symbol.  
  
<a id="enswapdays"></a>
## EnSwapDays (#enswapdays)

Triple swap charging days are enumerated in EnSwapDays.

ID | Value | Description  
SWAP_DAY_SUNDAY | 0 | Sunday.  
SWAP_DAY_MONDAY | 1 | Monday.  
SWAP_DAY_TUESDAY | 2 | Tuesday.  
SWAP_DAY_WEDNESDAY | 3 | Wednesday.  
SWAP_DAY_THURSDAY | 4 | Thursday.  
SWAP_DAY_FRIDAY | 5 | Friday.  
SWAP_DAY_SATURDAY | 6 | Saturday.  
SWAP_DAY_DISABLED | 7 | Triple swaps are disabled.  
  
<a id="enswapflags"></a>
## EnSwapFlags (#enswapflags)

Additional swap settings are enumerated in EnSwapFlags.

ID | Value | Description  
SWAP_FLAGS_NONE | 0 | Additional settings are not used.  
SWAP_FLAGS_CONSIDER_HOLIDAYS | 1 | Account for holidays when calculating swaps. If the flag is enabled, the platform checks all [holiday](../../../../Platform-Setup/Holidays.md) configurations. The day before the holiday, the swap is doubled. No swap is charged on the day of the holiday.  
  
<a id="eninstantmode"></a>
## EnInstantMode (#eninstantmode)

Types of check for the instant execution mode are enumerate in EnInstantMode.

ID | Value | Description  
INSTANT_CHECK_NORMAL | 0 | The normal mode of instant execution.  
  
<a id="enrequestflags"></a>
## EnRequestFlags (#enrequestflags)

Options of the Request execution mode are enumerated in EnRequestFlags.

ID | Value | Description  
REQUEST_FLAGS_NONE | 0 | No flags.  
REQUEST_FLAGS_ORDER | 1 | Additional confirmation mode.  
  
<a id="entradeflags"></a>
## EnTradeFlags (#entradeflags)

Trade flags of symbols are enumerated in EnTradeFlags.

ID | Value | Description  
TRADE_FLAGS_NONE | 0 | Beginning of enumeration. Corresponds to the absence of flags.  
TRADE_FLAGS_PROFIT_BY_MARKET | 1 | This flag is used for the Forex type symbols only ([TRADE_MODE_FOREX (#enexpirationflags)](Enumerations.md#enexpirationflags)). By default for the conversion of profit/loss from the profit currency to the deposit currency, the price at which a deal (exit from position) is performed is used, the profitability/unprofitability of the deal is not taken into consideration. If this flag is enabled, the conversion is performed using the current Bid/Ask price depending of the profitability/unprofitability of a deal. The Bid price is taken for calculations for profitable deals, because as a result of a profitable deal, a trader obtains a certain amount of the profit currency and needs to sell it for the deposit currency. The Ask price is taken for losing deals, because as a result of a losing deal, a trader needs to buy a certain amount of currency for the deposit currency.  
TRADE_FLAGS_ALLOW_SIGNALS | 2 | If this flag is not enabled, clients will not be able to copy trade operations by this symbol using the [Signals](https://www.mql5.com/en/signals) service. Trading signals can also be disabled on a client group level ([EnTradeFlags (#entradeflags)](../mt5-groups/Enumerations.md#entradeflags)).  
  
<a id="enorderflags"></a>
## EnOrderFlags (#enorderflags)

Flags of [orders](../mt5-orders.md) that are allowed for the symbol are enumerated in EnOrderFlags.

Identifier | Value | Description  
ORDER_FLAGS_NONE | 0 | Beginning of enumeration. Corresponds to the absence of flags.  
ORDER_FLAGS_MARKET | 1 | Market orders Buy and Sell are allowed.  
ORDER_FLAGS_LIMIT | 2 | Limit orders Buy Limit and Sell Limit are allowed.  
ORDER_FLAGS_STOP | 4 | Stop orders Buy Stop and Sell Stop are allowed.  
ORDER_FLAGS_STOP_LIMIT | 8 | Stop Limit orders Buy Stop Limit and Sell Stop Limit are allowed.  
ORDER_FLAGS_SL | 16 | Stop Loss orders are allowed.  
ORDER_FLAGS_TP | 32 | Take Profit orders are allowed.  
ORDER_FLAGS_CLOSEBY | 64 | Orders to close a position by an opposite one ([OP_CLOSE_BY (#enordertype)](../mt5-orders/Enumerations.md#enordertype)) are allowed. Close By permission of a symbol does not mean that this type of orders will be available on netting accounts. Close By orders can only be used on [hedging accounts (#hedging)](../../../../Platform-Setup/Groups/Position-Accounting-Systems.md#hedging).  
  
<a id="enmargintypes"></a>
## EnMarginTypes (#enmargintypes)

Types of orders used for specified margin rates are enumerated in EnMarginTypes.

Identifier | Value | Description  
MARGIN_BUY | 0 | Market buy order.  
MARGIN_SELL | 1 | Market sell order.  
MARGIN_BUY_LIMIT | 2 | Buy Limit pending order.  
MARGIN_SELL_LIMIT | 3 | Sell Limit pending order.  
MARGIN_BUY_STOP | 4 | Buy Stop pending order.  
MARGIN_SELL_STOP | 5 | Sell Stop pending order.  
MARGIN_BUY_STOP_LIMIT | 6 | Buy Stop Limit pending order.  
MARGIN_SELL_STOP_LIMIT | 7 | Sell Stop Limit pending order.  
  
<a id="ensplicetype"></a>
## EnSpliceType (#ensplicetype)

Futures splicing types are available in EnSpliceType.

Identifier | Value | Description  
SPLICE_NONE | 0 | No splicing.  
SPLICE_UNADJUSTED | 1 | Splicing futures quotes "as is" — the price level of the previous contract is not adjusted to the current (front) contract prices.  
SPLICE_ADJUSTED | 2 | In this mode, a difference between the last quote of the previous contract and the first quote of the front contract is calculated. All quotes of the previous contract are then adjusted by this value. This makes a spliced chart look smooth without gaps between contracts.  
  
<a id="ensplicetimetype"></a>
## EnSpliceTimeType (#ensplicetimetype)

Futures splicing dates are available in EnSpliceTimeType.

Identifier | Value | Description  
SPLICE_TIME_EXPIRATION | 0 | Splicing at the very moment of instrument expiration TimeExpiration.  
  
<a id="ensectors"></a>
## EnSectors (#ensectors)

EnSectors lists economic sectors a trading instrument may belong to.

ID | Value | Description  
SECTOR_UNDEFINED | 0 | Undefined  
SECTOR_BASIC_MATERIALS | 1 | Basic materials  
SECTOR_COMMUNICATION_SERVICES | 2 | Communication services  
SECTOR_CONSUMER_CYCLICAL | 3 | Consumer cyclical  
SECTOR_CONSUMER_DEFENSIVE | 4 | Consumer defensive  
SECTOR_ENERGY | 5 | Energy  
SECTOR_FINANCIAL | 6 | Finance  
SECTOR_HEALTHCARE | 7 | Healthcare  
SECTOR_INDUSTRIALS | 8 | Industrials  
SECTOR_REAL_ESTATE | 9 | Real estate  
SECTOR_TECHNOLOGY | 10 | Technology  
SECTOR_UTILITIES | 11 | Utilities  
SECTOR_CURRENCY | 12 | Currency  
SECTOR_CURRENCY_CRYPTO | 13 | Crypto currency  
SECTOR_INDEXES | 14 | Indices  
SECTOR_COMMODITIES | 15 | Commodities  
  
<a id="enindustries"></a>
## EnIndustries (#enindustries)

EnIndustries lists industry branches a trading instrument may belong to.

ID | Value | Description  
INDUSTRY_UNDEFINED | 0 | Undefined  
Basic materials  
INDUSTRY_AGRICULTURAL_INPUTS | 1 | Agricultural inputs  
INDUSTRY_ALUMINIUM | 2 | Aluminium  
INDUSTRY_BUILDING_MATERIALS | 3 | Building materials  
INDUSTRY_CHEMICALS | 4 | Chemicals  
INDUSTRY_COKING_COAL | 5 | Coking coal  
INDUSTRY_COPPER | 6 | Copper  
INDUSTRY_GOLD | 7 | Gold  
INDUSTRY_LUMBER_WOOD | 8 | Lumber and wood production  
INDUSTRY_INDUSTRIAL_METALS | 9 | Other industrial metals and mining  
INDUSTRY_PRECIOUS_METALS | 10 | Other precious metals and mining  
INDUSTRY_PAPER | 11 | Paper and paper products  
INDUSTRY_SILVER | 12 | Silver  
INDUSTRY_SPECIALTY_CHEMICALS | 13 | Specialty chemicals  
INDUSTRY_STEEL | 14 | Steel  
INDUSTRY_BASIC_MATERIALS_FIRST | 1 | Beginning of the basic materials types enumeration. Corresponds to INDUSTRY_AGRICULTURAL_INPUTS.  
INDUSTRY_BASIC_MATERIALS_LAST | 14 | End of the basic materials types enumeration. Corresponds to INDUSTRY_STEEL.  
INDUSTRY_BASIC_MATERIALS_END | 50 | Basic materials types enumeration limit.  
Communication services  
INDUSTRY_ADVERTISING | 51 | Advertising agencies  
INDUSTRY_BROADCASTING | 52 | Broadcasting  
INDUSTRY_GAMING_MULTIMEDIA | 53 | Electronic gaming and multimedia  
INDUSTRY_ENTERTAINMENT | 54 | Entertainment  
INDUSTRY_INTERNET_CONTENT | 55 | Internet content and information  
INDUSTRY_PUBLISHING | 56 | Publishing  
INDUSTRY_TELECOM | 57 | Telecom services  
INDUSTRY_COMMUNICATION_FIRST | 51 | Beginning of the communication services types enumeration. Corresponds to INDUSTRY_ADVERTISING.  
INDUSTRY_COMMUNICATION_LAST | 57 | End of the communication services types enumeration. Corresponds to INDUSTRY_TELECOM.  
INDUSTRY_COMMUNICATION_END | 100 | Communication services types enumeration limit.  
Consumer cyclical  
INDUSTRY_APPAREL_MANUFACTURING | 101 | Apparel manufacturing  
INDUSTRY_APPAREL_RETAIL | 102 | Apparel retail  
INDUSTRY_AUTO_MANUFACTURERS | 103 | Auto manufacturers  
INDUSTRY_AUTO_PARTS | 104 | Auto parts  
INDUSTRY_AUTO_DEALERSHIP | 105 | Auto and truck dealerships  
INDUSTRY_DEPARTMENT_STORES | 106 | Department stores  
INDUSTRY_FOOTWEAR_ACCESSORIES | 107 | Footwear and accessories  
INDUSTRY_FURNISHINGS | 108 | Furnishing, fixtures and appliances  
INDUSTRY_GAMBLING | 109 | Gambling  
INDUSTRY_HOME_IMPROV_RETAIL | 110 | Home improvement retail  
INDUSTRY_INTERNET_RETAIL | 111 | Internet retail  
INDUSTRY_LEISURE | 112 | Leisure  
INDUSTRY_LODGING | 113 | Lodging  
INDUSTRY_LUXURY_GOODS | 114 | Luxury goods  
INDUSTRY_PACKAGING_CONTAINERS | 115 | Packaging and containers  
INDUSTRY_PERSONAL_SERVICES | 116 | Personal services  
INDUSTRY_RECREATIONAL_VEHICLES | 117 | Recreational vehicles  
INDUSTRY_RESIDENT_CONSTRUCTION | 118 | Residential construction  
INDUSTRY_RESORTS_CASINOS | 119 | Resorts and casinos  
INDUSTRY_RESTAURANTS | 120 | Restaurants  
INDUSTRY_SPECIALTY_RETAIL | 121 | Specialty retail  
INDUSTRY_TEXTILE_MANUFACTURING | 122 | Textile manufacturing  
INDUSTRY_TRAVEL_SERVICES | 123 | Travel services  
INDUSTRY_CONSUMER_CYCL_FIRST | 101 | Beginning of enumeration of industry branches related to production of goods and services of cyclical demand. Corresponds to INDUSTRY_APPAREL_MANUFACTURING.  
INDUSTRY_CONSUMER_CYCL_LAST | 123 | End of enumeration of industry branches related to production of goods and services of cyclical demand. Corresponds to INDUSTRY_TRAVEL_SERVICES.  
INDUSTRY_CONSUMER_CYCL_END | 150 | Limit of the enumeration of industry branches related to production of goods and services of cyclical demand.  
Consumer defensive  
INDUSTRY_BEVERAGES_BREWERS | 151 | Beverages - Brewers  
INDUSTRY_BEVERAGES_NON_ALCO | 152 | Beverages - Non-alcoholic  
INDUSTRY_BEVERAGES_WINERIES | 153 | Beverages - Wineries and distilleries  
INDUSTRY_CONFECTIONERS | 154 | Confectioners  
INDUSTRY_DISCOUNT_STORES | 155 | Discount stores  
INDUSTRY_EDUCATION_TRAINIG | 156 | Education and training services  
INDUSTRY_FARM_PRODUCTS | 157 | Farm products  
INDUSTRY_FOOD_DISTRIBUTION | 158 | Food distribution  
INDUSTRY_GROCERY_STORES | 159 | Grocery stores  
INDUSTRY_HOUSEHOLD_PRODUCTS | 160 | Household and personal products  
INDUSTRY_PACKAGED_FOODS | 161 | Packaged foods  
INDUSTRY_TOBACCO | 162 | Tobacco  
INDUSTRY_CONSUMER_DEF_FIRST | 151 | Beginning of enumeration of industry branches related to production of consumer defensive goods and services. Corresponds to INDUSTRY_BEVERAGES_BREWERS.  
INDUSTRY_CONSUMER_DEF_LAST | 162 | End of enumeration of industry branches related to production of consumer defensive goods and services. Corresponds to INDUSTRY_TOBACCO.  
INDUSTRY_CONSUMER_DEF_END | 200 | Limit of the enumeration of industry branches related to production of consumer defensive goods and services.  
Energy  
INDUSTRY_OIL_GAS_DRILLING | 201 | Oil and gas drilling  
INDUSTRY_OIL_GAS_EP | 202 | Oil and gas extraction and processing  
INDUSTRY_OIL_GAS_EQUIPMENT | 203 | Oil and gas equipment and services  
INDUSTRY_OIL_GAS_INTEGRATED | 204 | Oil and gas integrated  
INDUSTRY_OIL_GAS_MIDSTREAM | 205 | Oil and gas midstream  
INDUSTRY_OIL_GAS_REFINING | 206 | Oil and gas refining and marketing  
INDUSTRY_THERMAL_COAL | 207 | Thermal coal  
INDUSTRY_URANIUM | 208 | Uranium  
INDUSTRY_ENERGY_FIRST | 201 | Beginning of enumeration of energy industry types. Corresponds to INDUSTRY_OIL_GAS_DRILLING.  
INDUSTRY_ENERGY_LAST | 208 | End of enumeration of energy industry types. Corresponds to INDUSTRY_URANIUM.  
INDUSTRY_ENERGY_END | 250 | Limit of the energy industry types enumeration.  
Finance  
INDUSTRY_EXCHANGE_TRADED_FUND | 251 | Exchange traded fund  
INDUSTRY_ASSETS_MANAGEMENT | 252 | Assets management  
INDUSTRY_BANKS_DIVERSIFIED | 253 | Banks - Diversified  
INDUSTRY_BANKS_REGIONAL | 254 | Banks - Regional  
INDUSTRY_CAPITAL_MARKETS | 255 | Capital markets  
INDUSTRY_CLOSE_END_FUND_DEBT | 256 | Closed-End fund - Debt  
INDUSTRY_CLOSE_END_FUND_EQUITY | 257 | Closed-end fund - Equity  
INDUSTRY_CLOSE_END_FUND_FOREIGN | 258 | Closed-end fund - Foreign  
INDUSTRY_CREDIT_SERVICES | 259 | Credit services  
INDUSTRY_FINANCIAL_CONGLOMERATE | 260 | Financial conglomerates  
INDUSTRY_FINANCIAL_DATA_EXCHANGE | 261 | Financial data and stock exchange  
INDUSTRY_INSURANCE_BROKERS | 262 | Insurance brokers  
INDUSTRY_INSURANCE_DIVERSIFIED | 263 | Insurance - Diversified  
INDUSTRY_INSURANCE_LIFE | 264 | Insurance - Life  
INDUSTRY_INSURANCE_PROPERTY | 265 | Insurance - Property and casualty  
INDUSTRY_INSURANCE_REINSURANCE | 266 | Insurance - Reinsurance  
INDUSTRY_INSURANCE_SPECIALTY | 267 | Insurance - Specialty  
INDUSTRY_MORTGAGE_FINANCE | 268 | Mortgage finance  
INDUSTRY_SHELL_COMPANIES | 269 | Shell companies  
INDUSTRY_FINANCIAL_FIRST | 251 | Beginning of enumeration of the financial services types. Corresponds to INDUSTRY_EXCHANGE_TRADED_FUND.  
INDUSTRY_FINANCIAL_LAST | 269 | End of enumeration of the financial services types. Corresponds to INDUSTRY_SHELL_COMPANIES.  
INDUSTRY_FINANCIAL_END | 300 | Limit of the financial services types enumeration.  
Healthcare  
INDUSTRY_BIOTECHNOLOGY | 301 | Biotechnology  
INDUSTRY_DIAGNOSTICS_RESEARCH | 302 | Diagnostics and research  
INDUSTRY_DRUGS_MANUFACTURERS | 303 | Drugs manufacturers - general  
INDUSTRY_DRUGS_MANUFACTURERS_SPEC | 304 | Drugs manufacturers - Specialty and generic  
INDUSTRY_HEALTHCARE_PLANS | 305 | Healthcare plans  
INDUSTRY_HEALTH_INFORMATION | 306 | Health information services  
INDUSTRY_MEDICAL_FACILITIES | 307 | Medical care facilities  
INDUSTRY_MEDICAL_DEVICES | 308 | Medical devices  
INDUSTRY_MEDICAL_DISTRIBUTION | 309 | Medical distribution  
INDUSTRY_MEDICAL_INSTRUMENTS | 310 | Medical instruments and supplies  
INDUSTRY_PHARM_RETAILERS | 311 | Pharmaceutical retailers  
INDUSTRY_HEALTHCARE_FIRST | 301 | Beginning of enumeration of healthcare services types. Corresponds to INDUSTRY_BIOTECHNOLOGY.  
INDUSTRY_HEALTHCARE_LAST | 311 | End of enumeration of healthcare services types. Corresponds to INDUSTRY_PHARM_RETAILERS.  
INDUSTRY_HEALTHCARE_END | 350 | Limit of the healthcare services types enumeration.  
Industrials  
INDUSTRY_AEROSPACE_DEFENSE | 351 | Aerospace and defense  
INDUSTRY_AIRLINES | 352 | Airlines  
INDUSTRY_AIRPORTS_SERVICES | 353 | Airports and air services  
INDUSTRY_BUILDING_PRODUCTS | 354 | Building products and equipment  
INDUSTRY_BUSINESS_EQUIPMENT | 355 | Business equipment and supplies  
INDUSTRY_CONGLOMERATES | 356 | Conglomerates  
INDUSTRY_CONSULTING_SERVICES | 357 | Consulting services  
INDUSTRY_ELECTRICAL_EQUIPMENT | 358 | Electrical equipment and parts  
INDUSTRY_ENGINEERING_CONSTRUCTION | 359 | Engineering and construction  
INDUSTRY_FARM_HEAVY_MACHINERY | 360 | Farm and heavy construction machinery  
INDUSTRY_INDUSTRIAL_DISTRIBUTION | 361 | Industrial distribution  
INDUSTRY_INFRASTRUCTURE_OPERATIONS | 362 | Infrastructure operations  
INDUSTRY_FREIGHT_LOGISTICS | 363 | Integrated freight and logistics  
INDUSTRY_MARINE_SHIPPING | 364 | Marine shipping  
INDUSTRY_METAL_FABRICATION | 365 | Metal fabrication  
INDUSTRY_POLLUTION_CONTROL | 366 | Pollution and treatment controls  
INDUSTRY_RAILROADS | 367 | Railroads  
INDUSTRY_RENTAL_LEASING | 368 | Rental and leasing services  
INDUSTRY_SECURITY_PROTECTION | 369 | Security and protection services  
INDUSTRY_SPEALITY_BUSINESS_SERVICES | 370 | Specialty business services  
INDUSTRY_SPEALITY_MACHINERY | 371 | Specialty industrial machinery  
INDUSTRY_STUFFING_EMPLOYMENT | 372 | Stuffing and employment services  
INDUSTRY_TOOLS_ACCESSORIES | 373 | Tools and accessories  
INDUSTRY_TRUCKING | 374 | Trucking  
INDUSTRY_WASTE_MANAGEMENT | 375 | Waste management  
INDUSTRY_INDUSTRIALS_FIRST | 351 | Beginning of enumeration of industry types. Corresponds to INDUSTRY_AEROSPACE_DEFENSE.  
INDUSTRY_INDUSTRIALS_LAST | 375 | End of enumeration of industry types. Corresponds to INDUSTRY_WASTE_MANAGEMENT.  
INDUSTRY_INDUSTRIALS_END | 400 | Limit of the industry types enumeration.  
Real estate  
INDUSTRY_REAL_ESTATE_DEVELOPMENT | 401 | Real estate - Development  
INDUSTRY_REAL_ESTATE_DIVERSIFIED | 402 | Real estate - Diversified  
INDUSTRY_REAL_ESTATE_SERVICES | 403 | Real estate services  
INDUSTRY_REIT_DIVERSIFIED | 404 | REIT - Diversified  
INDUSTRY_REIT_HEALTCARE | 405 | REIT - Healthcase facilities  
INDUSTRY_REIT_HOTEL_MOTEL | 406 | REIT - Hotel and motel  
INDUSTRY_REIT_INDUSTRIAL | 407 | REIT - Industrial  
INDUSTRY_REIT_MORTAGE | 408 | REIT - Mortgage  
INDUSTRY_REIT_OFFICE | 409 | REIT - Office  
INDUSTRY_REIT_RESIDENTAL | 410 | REIT - Residential  
INDUSTRY_REIT_RETAIL | 411 | REIT - Retail  
INDUSTRY_REIT_SPECIALITY | 412 | REIT - Specialty  
INDUSTRY_REAL_ESTATE_FIRST | 401 | Beginning of enumeration of the real estate services types. Corresponds to INDUSTRY_REAL_ESTATE_DEVELOPMENT.  
INDUSTRY_REAL_ESTATE_LAST | 412 | End of enumeration of the real estate services types. Corresponds to INDUSTRY_REIT_SPECIALITY.  
INDUSTRY_REAL_ESTATE_END | 450 | Limit of the real estate services types enumeration.  
Technology  
INDUSTRY_COMMUNICATION_EQUIPMENT | 451 | Communication equipment  
INDUSTRY_COMPUTER_HARDWARE | 452 | Computer hardware  
INDUSTRY_CONSUMER_ELECTRONICS | 453 | Consumer electronics  
INDUSTRY_ELECTRONIC_COMPONENTS | 454 | Electronic components  
INDUSTRY_ELECTRONIC_DISTRIBUTION | 455 | Electronics and computer distribution  
INDUSTRY_IT_SERVICES | 456 | Information technology services  
INDUSTRY_SCIENTIFIC_INSTRUMENTS | 457 | Scientific and technical instruments  
INDUSTRY_SEMICONDUCTOR_EQUIPMENT | 458 | Semiconductor equipment and materials  
INDUSTRY_SEMICONDUCTORS | 459 | Semiconductors  
INDUSTRY_SOFTWARE_APPLICATION | 460 | Software - Application  
INDUSTRY_SOFTWARE_INFRASTRUCTURE | 461 | Software - Infrastructure  
INDUSTRY_SOLAR | 462 | Solar  
INDUSTRY_TECHNOLOGY_FIRST | 451 | Beginning of enumeration of high-tech industry types. Corresponds to INDUSTRY_COMMUNICATION_EQUIPMENT.  
INDUSTRY_TECHNOLOGY_LAST | 462 | End of enumeration of high-tech industry types. Corresponds to INDUSTRY_SOLAR.  
INDUSTRY_TECHNOLOGY_END | 500 | Limit of the high-tech industry types enumeration.  
Utilities  
INDUSTRY_UTILITIES_DIVERSIFIED | 501 | Utilities - Diversified  
INDUSTRY_UTILITIES_POWERPRODUCERS | 502 | Utilities - Independent power producers  
INDUSTRY_UTILITIES_RENEWABLE | 503 | Utilities - Renewable  
INDUSTRY_UTILITIES_REGULATED_ELECTRIC | 504 | Utilities - Regulated electric  
INDUSTRY_UTILITIES_REGULATED_GAS | 505 | Utilities - Regulated gas  
INDUSTRY_UTILITIES_REGULATED_WATER | 506 | Utilities - Regulated water  
INDUSTRY_UTILITIES_FIRST | 501 | Beginning of enumeration of utilities services types. Corresponds to INDUSTRY_UTILITIES_DIVERSIFIED.  
INDUSTRY_UTILITIES_LAST | 506 | End of enumeration of utilities services types. Corresponds to INDUSTRY_UTILITIES_REGULATED_WATER.  
INDUSTRY_UTILITIES_END | 550 | Limit of the utilities services types enumeration.  
Commodities  
INDUSTRY_COMMODITIES_AGRICULTURAL | 551 | Agriculture  
INDUSTRY_COMMODITIES_ENERGY | 552 | Energy  
INDUSTRY_COMMODITIES_METALS | 553 | Metals  
INDUSTRY_COMMODITIES_PRECIOUS | 554 | Precious metals  
INDUSTRY_COMMODITIES_FIRST | 551 | Beginning of enumeration of commodity types. Corresponds to INDUSTRY_COMMODITIES_AGRICULTURAL.  
INDUSTRY_COMMODITIES_LAST | 554 | End of enumeration of commodity types Corresponds to INDUSTRY_COMMODITIES_PRECIOUS.  
INDUSTRY_COMMODITIES_END | 600 | Limit of the commodity type enumeration.

```

---

<a id='backup-server-sql-export-mt5-users-enumerations-md'></a>
### 119. `Backup-Server/SQL-Export/mt5-users/Enumerations.md`

```markdown
[🏠 Document Start](../../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../../Platform-Components.md) / [Backup Server](../../../Backup-Server.md) / [SQL Export](../../SQL-Export.md) / [mt5_users](../mt5-users.md) / Enumerations

[Previous](../mt5-users.md) | [Next](../mt5-orders.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

To pass information about users the following enumerations are used:

  * [EnUsersRights (#enusersrights)](Enumerations.md#enusersrights)
  * [EnUsersPasswords (#enuserspasswords)](Enumerations.md#enuserspasswords)
  * [EnUsersConnectionTypes (#enusersconnectiontypes)](Enumerations.md#enusersconnectiontypes)
  * [EnSoActivation (#ensoactivation)](Enumerations.md#ensoactivation)



<a id="enusersrights"></a>
## EnUsersRights (#enusersrights)

Permissions that can be given to a user are enumerated in EnUsersRights.

ID | Value | Description  
USER_RIGHT_NONE | 0x0000000000000000 | No permissions.  
USER_RIGHT_ENABLED | 0x0000000000000001 | The user is allowed to connect.  
USER_RIGHT_PASSWORD | 0x0000000000000002 | The user is allowed to change the password.  
USER_RIGHT_TRADE_DISABLED | 0x0000000000000004 | Trading is disabled for the user.  
USER_RIGHT_INVESTOR | 0x0000000000000008 | Service value for internal use.  
USER_RIGHT_CONFIRMED | 0x0000000000000010 | User's certificate is confirmed.  
USER_RIGHT_TRAILING | 0x0000000000000020 | The user is allowed to use trailing stop.  
USER_RIGHT_EXPERT | 0x0000000000000040 | The user is allowed to use Expert Advisors.  
USER_RIGHT_OBSOLETE | 0x0000000000000080 | The flag is obsolete and is not used.  
USER_RIGHT_REPORTS | 0x0000000000000100 | The user is allowed to receive daily reports. If the permission is not enabled, daily reports are neither generated nor sent for the account.  
USER_RIGHT_READONLY | 0x0000000000000200 | Service value for internal use.  
USER_RIGHT_RESET_PASS | 0x0000000000000400 | The user must change password during the next connection.  
USER_RIGHT_OTP_ENABLED | 0x0000000000000800 | The user can use OTP authentication.  
USER_RIGHT_SPONSORED_HOSTING | 0x0000000000002000 | Brokers can pay the [virtual hosting](https://www.mql5.com/en/vps) fee for their customers. The service is extremely important for traders, and the opportunity to receive a VPS for free can give them a good reason to choose your company over competitors. The availability of a broker-sponsored VPS is controlled at the individual account level. Only if this flag is enabled, the appropriate payment plan will be shown to the trader in the client terminal. For more details, please read the [appropriate section (#sponsored)](https://support.metaquotes.net/en/docs/community/vps#sponsored).  
USER_RIGHT_API_ENABLED | 0x0000000000004000 | The user is allowed to connect via the Web API.  
USER_RIGHT_TECHNICAL | 0x0000000000010000 | Permission for convenient work with technical accounts. Disable it for testing accounts to hide them from all managers who do not have special [access to technical accounts (#technical-accounts)](../../../../Platform-Setup/Managers.md#technical-accounts). Such technical accounts can be confusing for the managers working with clients, in which case hiding them can be useful.  This permission affects the account visibility in the general account list in the Administrator and Manager terminals, as well as in the list of online accounts in the Manager terminal.  
USER_RIGHT_EXCLUDE_REPORTS | 0x0000000000020000 | Allows excluding an account from [server reports](../../../../Platform-Setup/Reports.md). Like the previous permission, it is used for convenient management of technical accounts.  
  
<a id="enuserspasswords"></a>
## EnUsersPasswords (#enuserspasswords)

Types of passwords are enumerated in EnUsersPasswords.

ID | Value | Description  
USER_PASS_MAIN | 0 | The master password.  
USER_PASS_INVESTOR | 1 | The investor password.  
USER_PASS_API | 2 | API password.  
  
<a id="enusersconnectiontypes"></a>
## EnUsersConnectionTypes (#enusersconnectiontypes)

Types of client connections are enumerated in EnUsersConnectionTypes:

ID | Value | Description  
USER_TYPE_CLIENT | 0 | Connection from a client terminal.  
USER_TYPE_CLIENT_WINMOBILE | 1 | Connection from a mobile terminal for Windows Mobile (under development).  
USER_TYPE_CLIENT_WINPHONE | 2 | Connection from a mobile terminal for Windows Phone 7 (under development).  
USER_TYPE_CLIENT_API_WEB | 3 | Connection via the client Web API.  
USER_TYPE_CLIENT_IPHONE | 4 | Connection from a mobile terminal for iPhone.  
USER_TYPE_CLIENT_ANDROID | 5 | Connection from a mobile terminal for Android (under development).  
USER_TYPE_CLIENT_BLACKBERRY | 6 | Connection from a mobile terminal for BlackBerry (under development).  
USER_TYPE_ADMIN | 32 | Connection from an administrator terminal.  
USER_TYPE_MANAGER | 33 | Connection from a manager terminal.  
USER_TYPE_MANAGER_API | 34 | Connection via the manager interface of the Manager API.  
USER_TYPE_ADMIN_API | 36 | Connection via the administrator interface of the Manager API.  
USER_TYPE_MANAGER_API_WEB | 37 | Connection via the manager Web API.  
  
<a id="ensoactivation"></a>
## EnSoActivation (#ensoactivation)

The account status as per the minimum amount of funds on the account required to maintain trading positions are enumerated in EnSoActivation.

ID | Value | Description  
ACTIVATION_NONE | 0 | None.  
ACTIVATION_MARGIN_CALL | 1 | Margin call.  
ACTIVATION_STOP_OUT | 2 | Stop out.

```

---

<a id='data-feeds-alliance-news-feeder-md'></a>
### 119. `Data-Feeds/Alliance-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Alliance News Feeder

[Previous](UniNewsFeeder.md) | [Next](Newsquawk.md)

# Alliance News Feeder

The data feed allows receiving financial news and analytics from the British [Alliance News](https://alliancenews.com/) agency. The service provides traders with extensive selection of news for making informed decisions when trading stocks, currencies, CFDs, options and futures. Alliance News covers over 2 400 companies, including FTSE giants, as well as smaller AIM participants and investment funds.

Blue-chip companies, British and international economic indicators, market reviews and broker ratings — [more than 500 daily news items](https://alliancenews.com/service/professional/) provide a complete picture of the day. News articles are written in an easy-to-understand way, while maintaining the high level of information content.

## Why Alliance News?

  * The core aim of the company is serving financial professionals and independent investors.
  * Founders have well over 50 years of financial news and technology experience.
  * Concise news service provides the most relevant information for trading without clutter.



## What The Alliance News Professional Service Offers Your Clients

  * News articles written in an easy-to-understand way, with the informed but not expert, reader in mind.
  * Blanket coverage of UK-listed companies and the global, political and macro-economic influences on their share prices.
  * Coverage of global blue-chip companies, as well as the forex and commodities markets.
  * Concise bullet point 'flash headline' reporting as the news unfolds, with full articles published soon thereafter.
  * Helps your clients get ideas, uncover opportunities and check facts while there is still money to be made.



## Ordering Subscription

Order subscription right from the [Buy](https://support.metaquotes.net/en/market/product/292) page of the technical support website. After submitting your request, managers of Alliance News will contact you and provide all information.

Another way is to send an email to [support@alliancenews.com](mailto:support@alliancenews.com) or call +44 207 199 0347.

## Configuration of the Data Feed

After requesting a subscription and receiving connection details from Alliance News, add the new Alliance News Feeder configuration via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of MetaTrader 5 Administrator:

![Alliance News Feeder setup](images/data_feed_alliance_server.png)

The following parameters should be specified on the [Common (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — AllianceNewsFeeder.
  * Feed server — URL of news feed server provided by Alliance News representatives. By default it is http://feedsv2.alliancenews.info:24413
  * Feed login — authorization login acquired from Alliance News representatives.
  * Password — authorization password acquired from Alliance News representatives.



> The port used for connection to Feed server must be allowed on the internal or external firewall of the server where the data feed is operating.

![Parameters](images/data_feed_alliance_parameters.png)

The data feed features the following additional [parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters):

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * News Request Period — the period of checking and downloading new information in seconds.



```

---

<a id='data-feeds-claws-horns-feeder-md'></a>
### 119. `Data-Feeds/Claws-&-Horns-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Claws & Horns Feeder

[Previous](Financial-Source-News-Feeder.md) | [Next](UniNewsFeeder.md)

# Claws & Horns Feeder

This data feed allows you to provide your clients with financial news and analytics from [Claws & Horns](https://www.clawshorns.com/):

  * economic calendar featuring all the important fundamental data
  * technical analysis
  * fundamental analysis
  * signals (market entry recommendations with entry/exit points that are updated throughout the day)
  * daily video podcasts with long-term outlook for the major currency pairs
  * daily analysis of Russian shares traded on the Moscow Exchange



Materials are provided in 15 languages, including Russian, English, Chinese, Spanish, French, German, etc.

Claws & Horns Feeder is free and included in the platform standard delivery. You can purchase subscription on the [Claws & Horns official website](https://www.clawshorns.com).

## Setup

Add the new Claws & Horns Feeder data source configuration via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of MetaTrader 5 Administrator:

![Claws & Horns Feeder setup](images/clawshorns_common.png)

The following parameters should be specified on the [Common (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data source:

  * Module — ClawsHornsFeeder64.
  * Feed server — Claws & Horns server address. api.clawshorns.com is set by default. There is no need to change it.
  * Password — when purchasing the subscription, you receive a special ID (token) consisting of 32 symbols. Enter it here.



![Claws & Horns Feeder parameters](images/clawshorns_param.png)

On the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab, you can also use an additional parameter "News Category" — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).

The client terminals will start receiving news right after enabling the data source. The data source [journal](../../Platform-Setup/Data-Feeds/Journal-of.md) can be requested to check its operation.

```

---

<a id='data-feeds-dj-news-feeder-md'></a>
### 119. `Data-Feeds/DJ-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / DJ News Feeder

[Previous](Dow-Jones-Prime-Tass-News-Feeder.md) | [Next](IQFeeder.md)

# DJ News Feeder

DJ News Feeder (DJNewsFeeder.exe) is the news feeder from the world-famous news agency Dow Jones. Dow Jones Newswires include comprehensive reviews and analytical materials, macroeconomic events and speeches of officials, rolling market commentary and expert analysis, company reports, breaking news and much more.

## How it works

To start receiving news, you should request a subscription at <https://www.dowjones.com>. In a contract with the news provider, you will receive the port number for the data feed to listen to. Specify this port number in data feed settings. You should also receive the list of IP addresses, from which the new content will be provided. These addresses must also be specified in the data feed settings for additional security. Otherwise, the data feed will accept connections from any addresses at the specified port.

## Setup

![Common](images/data_feeds_server_dj.png)

Open the [Common (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed settings and set the DowJonesNewsFeeder module.

![Parameters](images/data_feeds_parameters_dj.png)

Additional settings should be configured in the [Parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab:

  * Listening Port — the port number, at which the data feed will listen to connections from the data provider. Available in an agreement with the news provider. 
  * White List — one or more IP addresses, from which connection to the data feed is allowed. If this parameter is not set, connection from any address is allowed.  
If the exact IP address is not known, you can identify it by requesting the [logs](../../Platform-Setup/Network-cluster/Journal.md) of the history server or the [data feed](../../Platform-Setup/Data-Feeds/Journal-of.md). The provider sends out news content, and if their address is not included in the list of allowed IPs, the data stream is blocked and an appropriate message is added to the journal. The logs also contain the address of the server, from which the data is sent. The log may look like this: address X.X.X.X is not white listed, disconnecting.
  * News Category — the category name for the newsletters received from the data feed. The category name can then be used for specifying news to be delivered to client [groups](../../Platform-Setup/Groups.md).



> It is recommended that you specify the provider's IP address in the WhiteList parameter. This will increase the safety of operation.

```

---

<a id='data-feeds-dow-jones-prime-tass-news-feeder-md'></a>
### 119. `Data-Feeds/Dow-Jones-Prime-Tass-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Dow Jones Prime Tass News Feeder

[Previous](../Data-Feeds.md) | [Next](DJ-News-Feeder.md)

# Dow Jones Prime Tass News Feeder

Dow Jones Prime Tass News Feeder (DJPrimeTassNewsFeeder.exe) is the news feeder for receiving [Dow Jones Newswires](https://1prime.ru/docs/product/dowjones/) from the Prime agency.

## How it works

To start receiving news, you should request a subscription at [https://www.1prime.ru/](https://1prime.ru/). You should provide to Ptime Tass the IP address, at which the data feed will operate. It will be added to the list of addresses, to which the provider sends news. The data feed will enable external connections for this IP address and will start receiving incoming news. This connection scheme does not require additional data (such as login and password).

## Setup

![Common](images/data_feeds_server_dj_prime.png)

Specification of the following parameters is required on the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed settings:

  * Module — DowJonesNewsFeeder;
  * Feed server — IP address (or domain name) and port that will be opened for receiving news from the news provider.



![Parameters](images/data_feeds_parameters_dj_prime.png)

On the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab, you can set:

  * Client IP — IP address for the news provider, from which connection to the data feed will be allowed. If the parameter is absent, connections from all addresses are allowed.  
If you do not know the exact IP address of the news provider, you can find it out by requesting the [journal](../../Platform-Setup/Network-cluster/Journal.md) of the history server or the data feed. The news provider sends information, and if their IP is not added to the list of allowed addresses, the data thread is blocked which is reflected in the journal. The address of the server the data is sent from is also specified in the entries.
  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).



> It is recommended to specify an allowed IP address in the ClientIP parameter. It increases the security of operation.

```

---

<a id='data-feeds-fxstreet-feeder-md'></a>
### 119. `Data-Feeds/FXstreet-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / FXstreet Feeder

[Previous](KnowledgeView-News-Feeder.md) | [Next](Financial-Source-News-Feeder.md)

# FXstreet Feeder

FXstreet Feeder for MetaTrader 5 provides your clients with financial news, as well as the data on technical analysis from the [FXstreet.com](https://www.fxstreet.com/ "FXstreet.com") financial web portal. The news are provided in eight languages: English, Russian, Arabic, Chinese, German, Indonesian, Spanish and Turkish.

FXstreet Feeder is free and included in the platform standard delivery. Contact FXstreet.com to subscribe to the news. Contact details can be found on the web portal at ["Contact Us"](https://www.fxstreet.com/info/contact-us "Contact FXstreet.com") section.

## Setup

Add the new FXstreet Feeder data feed configuration via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of MetaTrader 5 Administrator:

![FXstreet Feeder Setup](images/data_feeds_server_fxstreet.png)

The following parameters must be specified on the ["Common"](../../Platform-Setup/Data-Feeds/Configuration-of.md) tab of the data feed:

  * Module — FXstreetFeeder(64);
  * Feed server — FXstreet server address. subscriptions.fxstreet.com is set by default;
  * Feed login — login (or Client Key) for connection to FXstreet server. Submitted by FXstreet when concluding an agreement for providing news feed.



![FXstreet Feeder Parameters](images/data_feeds_parameters_fxstreet.png)

Specify additional settings in the [Parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab:

  * Language — the language in which you wish to receive news. For each language, create a separate "Language" parameter with the appropriate value. For example, in order to receive news in English and Russian, you need to create two parameters: Language = english, Language = russian. If no language is specified, the datafeed will only deliver news in English.  
The following languages are supported:
    * arabic
    * chinese
    * english
    * french
    * german
    * indonesian
    * russian
    * spanish
    * thai
    * tradchinese
    * turkish
    * japanese
    * vietnamese
  * News Type — the type of news you wish to receive:
    * News — standard subscription.
    * FXBeat — news from famous Forex market participants featuring their personal opinion. To receive such newsletters, contact FXStreet.com for an appropriate subscription. FXStreet.com will provide a new Client Key or include the FXBeat subscription into the key your are using.
    * Crypto — cryptocurrency market news.
  * News Category — the category name for the newsletters received from the data feed. The category name can then be used for specifying news to be delivered to client [groups](../../Platform-Setup/Groups.md).



The client terminals will start receiving news right after enabling the data feed. The data feed [logs](../../Platform-Setup/Data-Feeds/Journal-of.md) can be requested to check its operation.

```

---

<a id='data-feeds-financial-source-news-feeder-md'></a>
### 119. `Data-Feeds/Financial-Source-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Financial Source News Feeder

[Previous](FXstreet-Feeder.md) | [Next](Claws-&-Horns-Feeder.md)

# Financial Source News Feeder

Financial Source News Feeder enables the real-time delivery of news related to global currencies as well as trading analytics. In their <https://financialsource.co> website, Forex News state that they aim to be the first to deliver forex news to users and bring high probability trading opportunities. Their professional analysts scour global newswires so you catch every currency move.

Financial Source news items are divided into the following categories: Central Banks, Market Insights, Must Read, Order Flow Levels and Risk Events. The size of news items ranges from brief informative reports to copyright analytical articles, which describe the full picture of the global market.

The data feed module is free and is included in the platform standard delivery package. To start receiving news, you should request a subscription via the [official website](https://financialsource.co/). After that you will be provided with an Authorization Token for the data feed configuration.

## Setup

Add the new Financial Source News Feeder configuration via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of MetaTrader 5 Administrator:

![Financial Source News Feeder setup](images/financialsource_common.png)

The following parameters should be specified on the [Common (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data source:

  * Module — ForexSourceNewsFeeder64.
  * Feed server — Financial Source server address. https://server.financialsource.co is set by default.



![Financial Source News Feeder parameters](images/forexsource_param.png)

Specify the following settings in the Parameters tab:

  * Authorization Token — API Key, a special key to connect to the server. provided after subscribing to the news.
  * Language — the news language. For example, en for English, es for Spanish, it for Italian, ar for Arabic, ru for Russian, de for German. Please contact Financial Source for the full list of supported language. English is used by default.
  * Process Updates — the news items broadcasted by Financial Source may change over time. For example, they may be adjusted or clarified. If the parameter is set to "Yes", the data feed will process these changes and send new versions of these news items to the platform (earlier received news letters cannot be changed). If the parameter value is "No", the data feed will not process changes and this only initial news versions will be available in the trading platform. The default value is "Yes".
  * News Category — the category name for the newsletters received from the data feed. The category name can then be used for specifying news to be delivered to client [groups](../../Platform-Setup/Groups.md).



> In order to receive news in several languages, create several data source configurations.

The client terminals will start receiving news right after enabling the data source. The data source [journal](../../Platform-Setup/Data-Feeds/Journal-of.md) can be requested to check its operation.

```

---

<a id='data-feeds-forexpros-feeder-md'></a>
### 119. `Data-Feeds/ForexPros-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / ForexPros Feeder

[Previous](IBTimes-News-Feeder.md) | [Next](KnowledgeView-News-Feeder.md)

# ForexPros Feeder

ForexPros Feeder is a data feed that allows receiving financial news from ForexPros ([www.forexpros.com](https://www.forexpros.com)).

Information from this company is broadcast though web services. In order to get access to these services, it is necessary to conclude a special agreement with ForexPros. The corresponding contact information is published on the [official website](https://www.forexpros.com/about-us/contact-us) of this company.

After signing the contract, you will be given a login and password. Use these data to configure the data feed.

## Setup

![Common](images/data_feed_forexpros_server.png)

On the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed specify the following parameters:

  * Module — ForexProsFeeder;
  * Feed server — specify here one of the addresses of the data source, depending on the language of news:


  * News in English — www.forexpros.com;
  * News in Spanish — www.forexpros.es;
  * News in French — www.forexpros.fr;
  * News in German — www.forexpros.de;
  * News in Italian — www.forexpros.it;
  * News in Russian — www.forexpros.ru;
  * News in Arabic — www.forexpros.ae;
  * News in Hebrew — www.forexpros.co.il;
  * News in Dutch — nl.forexpros.com;
  * News in Galician — www.forexpros.com.pt;
  * News in Japanese — www.forexpros.jp;
  * News in Chinese — cn.forexpros.com;
  * News in Turkish — www.forexprostr.com;
  * Feed login — authorization login received after you've signed an agreement with the ForexPros company.
  * Password — authorization password received after you've signed an agreement with the ForexPros company.



![Parameters](images/data_feed_forexpros_parameters.png)

The data feed features the following additional [parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters):

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * News Request Period — the period of checking and downloading new information in seconds. During the first connection the data feed will receive all the available news items. Further checks for news are performed at the specified intervals.



```

---

<a id='data-feeds-ibtimes-news-feeder-md'></a>
### 119. `Data-Feeds/IBTimes-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / IBTimes News Feeder

[Previous](RSS-News-Feeder.md) | [Next](ForexPros-Feeder.md)

# IBTimes News Feeder

IBTimes News Feeder delivers FxWire Pro Forex news from [International Business Times](https://www.fxwirepro.com/). 

With an existing network of 13 newsrooms worldwide, IBTimes has the adequate infrastructure necessary to create a fresh and new professional FX newswire service. FxWire Pro is a precise and timely newswire service for the modern day Forex trader. Each trading day FxWire Pro publishes over 600 news items in real time to help traders understand market-moving forces and make better and quicker trading decision.

## Unique news feed for the modern-day FX trader

FxWire Pro was conceived to integrate perfectly into the most popular trading platforms 

  * Succinct News: Short, Concise and To-The-Point  
FxWire Pro by IBTimes publishes news in an innovative format that significantly minimizes the information overload faced by modern day traders. The published items are sub categorized into News, Quotes and where applicable, Analysis. Rather than having to browse through lengthy paragraphs, the end-user will find clear and concise bullet points. The key objective in the development of FxWire Pro has been to transfer the maximum amount of information to the trader in the least possible time frame. IBTimes is proud to present a newswire that has been praised by several leading industry's analysts and traders for its unique and useful format of publishing.
  * Expert Forex Analysts and Editors Filter Information Noise  
The editorial process at publishing news on FxWire Pro involves Expert FX analysts and editors who act as a strong knowledge filter to remove any news item that is deemed irrelevant to the Forex trader.



FxWire Pro's 600+ a-day rolling news in an innovative format allow traders to be completely on top of the financial markets, economic and geo-political developments across the globe in real time.

## News categories of FxWire Pro

The core areas covered by IBTimes' Professional Forex newswire service are:

  * Macro-Economy News & Data
  * Currencies Movement
  * Geo Politics
  * Real Time Economic Indicators
  * Treasury
  * Ratings
  * Money Market
  * Central Bank
  * Market Moving Talks
  * Media Round Ups & Picks
  * Generic FX Relevant News
  * Commodities
  * Stocks & Indices
  * Research Notes
  * Currencies covered: Major, minor and exotic currencies are covered as part of this service along with economic indicators in real-time from the major economies.



## Pre-setup

Information is broadcast via web service. To gain access to the web service, you should sign an agreement with International Business Times by sending a request via [App Store](https://support.metaquotes.net/en/market/product/288). You will receive a special login and password which should be used to set up the data feed in the platform.

## Setup

![Data feed setup](images/data_feeds_server_ibt.png)

On the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed specify the following parameters:

  * Module â IBTNewsFeeder;
  * Feed server â specify here one of the addresses of the data source, depending on the language of news:


  * News in English â http://www.fxwirepro.com/fxwire/xml/newswire.php
  * News in Chinese â http://www.fxwirepro.com/fxwire/cn/xml/newswire.php
  * News in Japanese â http://www.fxwirepro.com/fxwire/jp/xml/newswire.php
  * Feed login â authorization login received after you've signed an agreement with the International Business Times company.
  * Password â authorization password received after you've signed an agreement with the International Business Times company.



On the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab, you can specify additional settings:

  * News Category â the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * News Request Period â the period of checking and downloading new information in seconds. During the first connection the data feed will receive all the available news items. Further connections are established at the intervals set in this parameter, default period is 30 seconds. Contact IB Times support service for the best news request interval as it may vary for different clients.



> If you want to receive news in all the three languages, create three separate data feeds with different names in MetaTrader 5 Administrator. In the Server field specify the appropriate address, in the fields of login and password specify the details of your subscription allowing to receive news in the appropriate language.

```

---

<a id='data-feeds-iqfeeder-md'></a>
### 119. `Data-Feeds/IQFeeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / IQFeeder

[Previous](DJ-News-Feeder.md) | [Next](MetaTrader-4-Feeder.md)

# IQFeeder

The IQFeeder is designed for receiving news and price data from [IQFeed](https://www.iqfeed.net). The company offers brokers a wide range of services:

  * Real-time quotes for financial instruments traded on the US and Canadian exchanges: NYSE, NASDAQ and Canadian Securities Exchange, among others
  * Real-time quotes for Forex instruments
  * Level II data (order book)
  * More than 700 market stats/breadth indicators, most of which are updated every second
  * Up to 180 calendar days of tick history
  * More than 11 years of one-minute historical data
  * Fundamental data on US stocks
  * Real-time news from leading agencies



IQFeeder is free and is included in the standard platform delivery package. You only need to subscribe for the data by contacting [IQFeed](https://www.iqfeed.net) and then to configure the data feed in the platform.

## How It Works

IQFeed provides a special software (IQFeed Client) that is responsible for information delivery from the provider to the local server where this software is installed. These data are translated to the history server via the IQFeeder data feed. Interaction between the data feed and the IQFeed client is implemented through the local IP address 127.0.0.1.

IQFeed Client is already available in the data feed. During data feed configuration in the platform, the required components will be installed automatically and thus no additional installation will be required.

## Setup

IQFeed provides data for a variety of trading instruments. In order to be able to receive relevant data, you need to [create corresponding symbols](../../Platform-Setup/Symbols.md). If you want to receive the order book in addition to quotes, enable the appropriate option in symbol settings:

![Enabling the Market Depth in trading symbol settings](images/iq_feed_symbol_dom.png)

Set a value other than "off" for the Market Depth parameter. If the initial depth of the Market Depth is different, the data feed will automatically align it with the value specified in the symbol settings in the platform. The price accuracy in the Market Depth will be automatically adjusted to the value specified in symbol settings.

> If symbol names on you platform side differ from those available in IQFeed, you can match corresponding symbols in the data feed settings, under the "[Translation (#translation)](../../Platform-Setup/Data-Feeds/Configuration-of.md#translation)" settings.

Once you have prepared the symbols, create a new [data feed configuration](../../Platform-Setup/Data-Feeds.md) for IQFeeder.

![Server](images/data_feeds_server_iq.png)

The following parameters should be specified on the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — IQFeeder.
  * Feed server — 127.0.0.1, this address is used to implement connection between the data feed and the IQFeed client, it cannot be changed.
  * Feed login — login for connection, which is provided by IQFeed upon subscription
  * Password — password for connection, which is provided by IQFeed upon subscription.



![Parameters](images/data_feeds_parameters_iq.png)

On the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab, specify "Product ID" that was received from the news provider and additional settings (if needed).

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Product — product identifier. It is provided by IQ Feed upon subscription.
  * L2 Realtime — set "Yes" to be able to receive the Market Depth data. Access to the relevant data must be granted by your IQFeed subscription and the [Market Depth feature must be allowed (#dom)](../../Platform-Setup/Symbols/Symbol-Settings/Common.md#dom) in symbol settings on the platform side.
  * Download Tick History — if set to "Yes", the data feed will download the available tick history of trading instruments.
  * Download M1 History — if set to "Yes", the data feed will download the available one-minute history of trading instruments.
  * Download D1 History — if set to "Yes", the data feed will download the available daily history for trading instruments. If this parameter is enabled along with the "Download M1 History" option, the daily history will only be downloaded for the periods for which one-minute history is not available.
  * Admin Port, Lookup Port, L1 Port, L2 Port, History Port — the ports on which IQFeed Client waits for incoming connections to feed appropriate data (L1 and L2 prices, quoting history). The default values correspond to IQFeed Client ports.
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



Before importing the price history, check the list of symbols configured in the data feed. If the data feed is allowed to download history, it will replace the history of all symbols within the platform, for which the data feed has permissions.

![Setup of symbol access for the data feed](images/iq_feed_symbols.png)

```

---

<a id='data-feeds-knowledgeview-news-feeder-md'></a>
### 119. `Data-Feeds/KnowledgeView-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / KnowledgeView News Feeder

[Previous](ForexPros-Feeder.md) | [Next](FXstreet-Feeder.md)

# KnowledgeView News Feeder

KnowledgeView News Feeder is designed to receive news from [KnowledgeView](https://www.knowledgeview.co.uk/), a partner of [Dow Jones](https://www.dowjones.com/). It allows to receive news in real time in three languages: Arabic, Farsi and Turkish.

If you want to start getting the news, you need to contact KnowledgeView or Dow Jones to sign the agreement. The contact information can be found on the official websites of these companies: [Offices](https://www.knowledgeview.co.uk/aboutus/offices "Offices") section of the KnowledgeView official web site and [Contact Us](https://www.dowjones.com/contactus/contactus.aspx?sect= "Contact Us") section of the Dow Jones official web site. After concluding the contract you will receive the parameters for connecting a data feed to KnowledgeView server: address, login, password and additional Filter parameter.

## Setup

Add the new KnowledgeView News Feeder data feed configuration via the [corresponding section of the administrator terminal](../../Platform-Setup/Data-Feeds.md).

![Common](images/data_feeds_server_kw.png)

The following parameters must be specified on the ["Common"](../../Platform-Setup/Data-Feeds/Configuration-of.md) tab of the data feed:

  * Module — KnowledgeViewNewsFeeder(64);
  * Feed server — KnowledgeView server web address. The default web address is http://fareeda.info/newsbrowser/api.
  * Feed login — login for connection to KnowledgeView server;
  * Password — password for connection to KnowledgeView server.



> Address, login and password are submitted by KnowledgeView during the agreement conclusion. A separate login and password are submitted for each news language. Thus, you should create several configurations for that data feed to get news in several languages simultaneously.

![Parameters](images/data_feeds_parameters_kw.png)

Specify the following parameters in the [Parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab:

  * News Request Period — intervals to check and download new data in seconds. The data feed receives all available news during the first connection. After that, the latest news are checked at the specified intervals. The lower the value, the faster the news will appear in the platform. But this will increase the network load. The default value is 60 seconds.
  * News Filter — the value is provided by KnowledgeView upon the execution of an agreement. Separate Filter parameter value is specified for each news language in the same way as it is done with a login and a password.
  * News Max — the maximum number of news items which can received by the data feed. If this parameter value is low while "News Request Period" is large, some of the news items provided by the source can be lost. The default value is 128.
  * News Category — the category name for the newsletters received from the data feed. The category name can then be used for specifying news to be delivered to client [groups](../../Platform-Setup/Groups.md).



If the Filter value is incorrect, the data feed will not be able to connect to the server. These parameters can be checked in the [data feed log](../../Platform-Setup/Data-Feeds/Journal-of.md):

2012.03.28 09:59:59 Gateway datafeed initialized, connecting to http://fareeda.info/newsbrowser/api   
2012.03.28 09:59:59 Gateway available datafeed filter: 'Forex Turkish'   
2012.03.28 09:59:59 Gateway available datafeed filter: 'Forex Turkish - month'   
2012.03.28 09:59:59 Gateway specified filter 'Turkish' is incorrect, check datafeed parameters   
2012.03.28 09:59:59 Gateway filter checking failed  
---  
  
In addition to the entries indicating the errors in the filter specification, the data feed log also displays available filter values (the entries of "available datafeed filter" type). The terminal will start receiving news right after the successful connection.

```

---

<a id='data-feeds-metatrader-4-feeder-md'></a>
### 119. `Data-Feeds/MetaTrader-4-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / MetaTrader 4 Feeder

[Previous](IQFeeder.md) | [Next](MetaTrader-5-Feeder.md)

# MetaTrader 4 Feeder

MetaTrader 4 Feeder is the data feed that enables receipt of quotes and news from MetaTrader 4 servers. This solution is built into the platform, which ensures minimal delays in quote delivery.

## How It Works

The data feed creates a common client connection with any MetaTrader 4 server, authorizing using a login and a password.

  * Connection can be established using any account (demo or real).
  * You can receive only quotes and news that are available to the account that is used for connection.

  
---  
  
## Automatic Opening of Demo Accounts

The data feed is capable of automatic of opening of demo accounts on the source server.

If the account details (login and password) are not specified in the data feed settings or the account has become invalid (expired), the data feed will open a new demo account and will use it for connecting.

## Setup

The data feed must be added via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of the administrator terminal.

![Common](images/data_feed_mt4_common.png)

The following parameters should be specified on the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — MetaTrader4Feeder;
  * Feed server — address of the MetaTrader 4 server and the port number to connect to it (separated by a colon);
  * Feed login — login (account number) for the authorization on the server;
  * Password — password of the account for the authorization on the server.



![Parameters](images/data_feed_mt4_parameters.png)

The data feed features the following additional [parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters):

  * Language — the language to be used for the news with their language not specified on the source server. This is necessary for correct conversion and further sorting of such news. "English" is applied by default. The language should be specified in the format standard for the Windows operating systems, though without the regional dialectic specifications. E.g. English, Russian, etc.
  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



```

---

<a id='data-feeds-metatrader-5-feeder-md'></a>
### 119. `Data-Feeds/MetaTrader-5-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / MetaTrader 5 Feeder

[Previous](MetaTrader-4-Feeder.md) | [Next](Trading-Central-News-Feeder.md)

<a id="metatrader-5-feeder"></a>
# MetaTrader 5 Feeder (#metatrader-5-feeder)

MetaTrader 5 Feeder is a data feed which enables the delivery of news, quotes and Market Depth data from any MetaTrader 5 servers.

This solution is built into the platform, which ensures minimal delays in quote delivery. To speed up data delivery, the data feed operates works in multiple streams, and also it automatically selects the best access points for connection.

<a id="setup"></a>
## Setup (#setup)

Contact the desired broker and agree on data delivery terms and conditions. To connect to the source broker, you will need a regular trading account (demo or real), with access to the required news and trading instruments. The data feed will create a client connection and will deliver data through this connection.

The data feed must be added via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of the administrator terminal.

![Common](images/data_feeds_server_mt5.png)

The following parameters should be specified on the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — MetaTrader5Feeder;
  * Feed server — address of the MetaTrader 5 server and the port number to connect to it (separated by a colon);
  * Feed login — login (account number) for the authorization on the server;
  * Password — password for the authorization. If the extended authorization mode is enabled on the server you are going to receive data from, you should use an investor password instead of the main one. Otherwise connection will be impossible.



![Parameters](images/data_feeds_parameters_mt5.png)

The data feed features the following additional [parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters):

  * Quotes Time Original — if "Yes", the datafeed itself sets the time for ticks considering the time zone of the recipient trade server. If the parameter is absent or set to "No", the time for ticks is set by the history server according to the trade time used.
  * Selftitled Translations — this parameter is used to prevent quotes from looping when connecting to the server on which the datafeed is installed. The default value is No. For more details please see [below (#retranslation)](MetaTrader-5-Feeder.md#retranslation).
  * Symbols Update — mode applied to the import of trading instruments to the platform from an external source. If set to No (default), the data feed will only add symbols from the source server that do not yet exist in the platform. If set to Yes, the data feed will also update the settings of already existing symbols, which may affect the broadcasting of quotes (general description, currency data, accuracy, order book depth, tick value and size, accrued interest on bond, settlement price, price limits, splicing data, and quoting sessions). Settings are updated in real time. Quoting sessions are updated taking into account server time zones.  
Symbol settings are only imported/updated, if the [appropriate option (#import)](../../Platform-Setup/Data-Feeds/Configuration-of.md#import) is enabled in the data feed settings.
  * Symbols Path — path to import trading instruments to. If this parameter is absent (by default), the data feed will import trading instruments into the \Preliminary subgroup with the trading option disabled. If this parameter has a non-empty value, the data feed will import trading instruments into the specified location.
  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



<a id="automatic-opening-of-demo-accounts"></a>
## Automatic Opening of Demo Accounts (#automatic-opening-of-demo-accounts)

The data feed is capable of automatic of opening of demo accounts on the source server.

If the account details (login and password) are not specified in the data feed settings or the account has become invalid (expired), the data feed will open a new demo account and will use it for connecting.

<a id="transferring-quotes"></a>
## Transferring quotes (#transferring-quotes)

For symbols with the [disabled market depth (#dom)](../../Platform-Setup/Symbols/Symbol-Settings/Common.md#dom) (on the external server side), MetaTrader 5 Feeder passes ticks with Bid and Ask prices.

For symbols with the enabled market depth, the data feed transfers the market depth changes as well as ticks with Last prices and volumes. Ticks containing only Bid and Ask price changes are not transferred. If the best supply and demand prices change in the market depth, the history server generates the necessary tick with Bid and Ask prices and adds it to the flow.

The data feed features the built-in switching mechanism to prevent the quote flow from stopping in case the external server stops transmitting the market depth changes. If not a single market depth change for a symbol arrives from the external system within 30 seconds, the data feed stops sorting out ticks having only Bid and Ask prices. In other words, it starts transferring to the platform both Last/Volume and Bid/Ask ticks.

The following entries are shown in the data feed journal when the market depth is no longer transmitted:

2017.09.12 15:20:25.412 Feeder books stream for EURUSD stopped (no books during 31 sec)   
2017.09.12 15:20:25.873 Feeder books stream for USDJPY stopped (no books during 31 sec)  
---  
  
If the flow is resumed:

2017.09.12 15:21:29.759 Feeder books stream for EURUSD resumed   
2017.09.12 15:21:30.060 Feeder books stream for USDJPY resumed  
---  
  
<a id="retranslation"></a>
## Symbol masks and own price retranslation (#retranslation)

In [datafeed translation settings (#translation)](../../Platform-Setup/Data-Feeds/Configuration-of.md#translation), the "*" mask can be used as the source symbol and as the destination symbol in the platform. For example, the settings Symbol="*", Source="*" mean that the names of the symbols will be used as they are provided in the external system. If the symbol is entitled EURUSD in the external system, then its data will be feed to the symbol with the same name on the trading platform side. The only situation in which such settings cannot be used is the connection of the data feed to the platform on which it is installed. In this case, receiving and feeding of quotes by the datafeed into the same symbols will lead to looping.

To avoid such situations, the datafeed provides the parameter "[Selftitled Translations (#selftitled-translations)](MetaTrader-5-Feeder.md#selftitled-translations)". If it is set to "No" (default) and the datafeed has a translation setting "*" <\- "*", the datafeed will not start. An appropriate entry will be added into the journal:

translation rule for symbols to themselves '* <\- *' not allowed but exists, remove this rule or allow it by 'Selftitled Translations' parameter  
---  
  
Before enabling this parameter, make sure that the data feed is not connected to the same cluster on which it is running. Otherwise, this can lead to quote looping in the platform.

```

---

<a id='data-feeds-metatrader-5-unifeeder-md'></a>
### 119. `Data-Feeds/MetaTrader-5-UniFeeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / MetaTrader 5 UniFeeder

[Previous](Trading-Central-News-Feeder.md) | [Next](Thomson-Reuters-Feeder.md)

# MetaTrader 5 UniFeeder

MetaTrader 5 UniFeeder is the data feed that enables receipt of quotes from the special utility — Universal DDE Connector. This solution is built into the platform, which ensures minimal delays in quote delivery.

## How It Works

Universal DDE Connector allows collecting quotes from different data feeds that support the DDE (Dynamic Data Exchange) protocol. The feeder translates quotes received from it to the MetaTrader 5 history server. More details about the Universal DDE Connector are given in a [separate section](Universal-DDE-Connector.md).

## Setup

The data feed must be added via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of the administrator terminal.

![MetaTrader 5 UniFeeder](images/data_feeds_server_uni.png)

The following parameters should be specified on the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — UniFeeder;
  * Feed server — address of the server where the Universal DDE Connector is installed and [port (#port)](Universal-DDE-Connector/Installation-and-Setup.md#port) for connecting to it, separated by a colon;
  * Feed login — [account (#account)](Universal-DDE-Connector/Installation-and-Setup.md#account), pre-created in the Universal DDE Connector;
  * Password — password of the account.



### Synthetic Quotes

MetaTrader 5 UniFeeder allows receiving quotes on symbols, whose data are not translated through Universal DDE Connector. This is achieved by way of mathematical conversion of other symbols' quotes translated through Universal DDE Connector. Such a calculation method can be applied to non-convertible currencies, whose exchange rate relative to convertible currencies is set by the central bank.

The calculation formulas for the quotes should be specified on the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab of the data feed:

![Parameters](images/data_feeds_parameters_uni.png)

Two fields are available here:

### Parameter

In the "Parameter" field, you should specify the symbol name and its price (Bid or Ask), that will be calculated according to the formula specified in the next field. The symbol name and the price type should be separated by a point, for example: GOLDVND.ask.

  * Symbol whose quotes are calculated must be present in the ["Symbols"](../../Platform-Setup/Symbols.md) section. Make sure that the two names match.
  * Calculation of both Bid and Ask prices is required for all symbols.

  
---  
  
### Value

In this field the calculation formula should be specified. You may use:

  * Symbols — any symbol, whose quotes are received from Universal DDE Connector can be used for calculations. But only one symbol for one formula can be used. Do not forget to specify the price type to use (Bid or Ask). For example, EURUSD.bid.



> A symbol that is used for calculation must exist in the trading platform. In addition, it must be added to the [list of symbols (#symbols)](../../Platform-Setup/Data-Feeds/Configuration-of.md#symbols), the quotes for which are translated by the data feed.

  * Simple mathematical calculations — multiplication (*), division (/), addition (+) and subtraction (-).
  * Brackets — you can use brackets "()" to define the calculation order.



  * You cannot use negative numbers in formulas. Thus "-3 + 5" is incorrect. The correct expression will be "5 - 3".
  * The separator of the integer and fractional part in formulas is also a point, irrespective of the operating system settings.
  * Only one symbol, whose quotes are received from Universal DDE Connector can be used in every formula.
  * Synthetic quotes calculated from other symbols cannot be used in formulas.

  
---  
  
## Additional Settings

On the "Parameters" tab, you can specify additional settings:

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



```

---

<a id='data-feeds-newsquawk-md'></a>
### 119. `Data-Feeds/Newsquawk.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Newsquawk

[Previous](Alliance-News-Feeder.md) | [Next](Remote-Datafeed.md)

# Newsquawk Feeder

Data feed for receiving financial newsletters from the [Newsquawk](https://newsquawk.com/) company. Newsquawk provides real-time access to the most important financial news, filtering data streams from hundreds of sources, such as Reuters, Bloomber and Daily Mail, among others. Additionally, you can receive daily market overviews across various categories of financial instruments, including forex, metals, stocks and commodities.

## Preparation

Fill our a form on the [Newsquawk website](https://www.newsquawk.com/sign_up.html). The company offers a free one-week trial subscription. After registration, you will receive a login/password or key to your email, which will be required to set up the data feed in the platform.

The built-in data feed module is already available in your platform. No fee is charged for the module use.

## Configuring the Data Feed

Add a new data feed configuration via the [corresponding section](../../Platform-Setup/Data-Feeds.md) of MetaTrader 5 Administrator:

![Create a data feed configuration and specify parameters](images/data_feed_newsquawk.png)

Specify the following parameters:

  * Feed server — news provider's server address. The default address is https://newsquawk.com. In most cases, there is no need to change it.
  * Feed login — login for connection provided by Newsquawk upon subscription.
  * Password — password for connection provided by Newsquawk upon subscription.
  * Authorization Token — key for connection provided by Newsquawk upon subscription. You can use either this parameter or Login/Password, depending on the credentials provided.
  * Language — a two-letter language code in ISO 639 format that will be included in incoming news. For example, en, es, pt, etc. It will be used to filter news by language on the client terminal side. Fill in this parameter in accordance with the language selected during subscription, that is, the language in which you actually receive the news. To receive news in different languages, create separate data source configurations.
  * Process Updates — Newsquawk may update and supplement previously published news. The parameter determines whether the data feed will transmit such updates to the platform. On the MetaTrader 5 side, each update will create additional news; previously transmitted news will not be changed. The default is "Yes" meaning updates are transmitted.
  * News Category — the category to which newsletters from the data source will be assigned. The category name can then be used for specifying news to be delivered to certain client [groups](../../Platform-Setup/Groups.md).



Once the data feed is enabled, client terminals will start receiving newsletters. To check the data feed operation, request its [logs](../../Platform-Setup/Data-Feeds/Journal-of.md).

```

---

<a id='data-feeds-rss-news-feeder-md'></a>
### 119. `Data-Feeds/RSS-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / RSS News Feeder

[Previous](Thomson-Reuters-Feeder.md) | [Next](IBTimes-News-Feeder.md)

# RSS News Feeder

The RSS News Feeder data feed enables the receipt of news from any sources that support the RSS channels. Such sources are various websites, as a rule.

For each source of news (each URL), you need to set up a separate [configuration](../../Platform-Setup/Data-Feeds.md) of RSS News Feeder data feed. During the first connection to a source, all the available news are downloaded and transferred. Further, requests for information updates are performed once in five minutes. Obtained information is cached on the hard drive. Therefore, only newly coming news items are downloaded if the data feed is turned on after standing idle for a while.

RSS News Feeder supports [categories (#categories)](../../MetaTrader-5-Administrator/User-Interface/Toolbox/News.md#categories) of incoming news, if any are implemented in the data source. All news items will be divided into subcategories of a category specified on the "Server" tab of the data feed settings.

> If you leave the "Category" field empty, the categories of incoming news will be written to the highest level. This may negatively affect the whole categorization of news received in the terminals.

## Setup

![Common](images/data_feeds_server_rss.png)

On the "Common" tab of the [data feed (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common), specify the following parameters:

  * Module — RSSNewsFeeder;
  * Feed server — address (url) of the data source. Additionally you can specify a port for connection separated with a colon from the address. If a port is not specified, port 80 is used on default.
  * Feed login — in case authentication is required for connecting to the data source, specify the login for connection in this field. Otherwise leave this field empty.
  * Password — in case authentication is required for connecting to the data source, specify the password for connection in this field. Otherwise leave this field empty.



![Parameters](images/data_feeds_parameters_rss.png)

The data feed features the following additional [parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters):

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * News Request Period — the period of checking and downloading new information in seconds.
  * Language — the language of news received from the data source. This parameters is necessary for correct conversion and further sorting of news. "English" is applied by default. The language should be specified in the format standard for the Windows operating systems, though without the regional dialectic specifications. E.g. English, Russian, etc.



```

---

<a id='data-feeds-remote-datafeed-md'></a>
### 119. `Data-Feeds/Remote-Datafeed.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Remote Datafeed

[Previous](Newsquawk.md) | [Next](Universal-DDE-Connector.md)

# Remote Datafeed

This option in the data feed [settings (#file)](../../Platform-Setup/Data-Feeds/Configuration-of.md#file) is intended for the connection of the server to a data feed located on a remote server. This data feed can be written using API.

![Remote Datafeed](images/remote_gateway.png)

In the parameters of connection to the data feed, the following needs to be specified:

  * Gateway server — the address of the server where the data feed is installed (module written using API, translating information from the provider), as well as the port number for connection, separated by a colon. For example, 192.168.0.180:443;
  * Gateway login — a login for connecting to the server;
  * Password — a password for connecting to the server;
  * Feed server — address of the data feed server;
  * Feed login — login to access the data feed server;
  * Password — password to access the data feed server.



```

---

<a id='data-feeds-thomson-reuters-feeder-md'></a>
### 119. `Data-Feeds/Thomson-Reuters-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Thomson Reuters Feeder

[Previous](MetaTrader-5-UniFeeder.md) | [Next](RSS-News-Feeder.md)

# Thomson Reuters Feeder

Thomson Reuters Feeder is a data feed that enables receiving of financial information from Thomson Reuters ([http://thomsonreuters.com](https://thomsonreuters.com "Thomson Reuters")).

Information from this company is transferred through web services. In order to get an access to them, you will need to conclude a special agreement. Please contact the company representative in your region. The corresponding contact information can be found on the company's website mentioned above.

Once the agreement is concluded, a user is given an IP address, login and password to access the service, as well as a unique ID (AppID). All this information must be provided when setting up the data feed in the administrator terminal.

## Setup

![ThomsonReutersFeeder](images/data_feeds_server_tr.png)

On the "Common" tab of [data feed (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common), specify the following parameters:

  * Module — ThomsonReutersFeeder;
  * Feed server — address of the server of Thomson Reuters and port to connect to it separated with colon. A port that is used for connecting, must support connection through the secured https protocol (SSL), usually port 443 is used;
  * Feed login — login to authorize on the server;
  * Password — password for the authorization.



  * IP address of the server, login and password are given when concluding the agreement.
  * A port that is used for the connection must be allowed on the server where the data feed is installed.

  
---  
  
![Parameters](images/data_feeds_parameters_tr.png)

On the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab, specify one parameter — "Application ID". This parameter is a unique identifier of an application that connects to the server of Thomson Reuters. Its value is also given when concluding the agreement.

News can be filtered by categories (topics) using additional optional parameters Ignore Topics Codes and Allow Topics Codes. To allow news from specified categories and disable all other news, specify the codes of the desired categories in the Allow Topics Codes parameter, separated by commas. To disable selected categories and enable all others, specify the categories to disable in Ignore Topics Codes, separated by commas. In the above example, the following codes are specified in Ignore Topics Codes:

  * SPO: sport
  * MSIC: music news
  * BLG: blogs



In this case, the datafeed will receive all news letters, except those from the specified categories.

Please note that a news item can relate to several categories. If the news belongs to at least one of the categories specified in the parameter, it will be filtered out.

  * The full list of topic codes can be obtained from Thomson Reuters.
  * News are filtered on Thomson Reuters side, the data feeds does not receive news by specified topics.

  
---  
  
Do not use the Language parameter to filter news. It won't affect the data feed. The filtration of news by language is set up in the [group configuration](../../Platform-Setup/Groups/Group-Settings.md). Some news from Thomson Reuters may be transmitted without indication of the language. In this case the news will be passed to the terminals regardless of the languages specified in the group settings.

### Additional Settings

On the "Parameters" tab, you can specify additional settings:

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



```

---

<a id='data-feeds-trading-central-news-feeder-md'></a>
### 119. `Data-Feeds/Trading-Central-News-Feeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Trading Central News Feeder

[Previous](MetaTrader-5-Feeder.md) | [Next](MetaTrader-5-UniFeeder.md)

# Trading Central News Feeder

Trading Central News Feeder is a data feed that enables receiving of analytical information on financial instruments from Trading Central ([www.tradingcentral.com](https://www.tradingcentral.com "Trading Central")). The basic activity of this company is the technical analysis trading recommendations sent by this company are based on.

Trading Central uses a FTP server to store data. In order to get access to these data, you should contact this company. To know the contact information, please visit the company's official website mentioned above. After you conclude an agreement, you are provided with the IP address of the FTP server, as well with the login and password for accessing it. Besides you will need to provide the IP address of your server (access server) in order for them to add it to the list of allowed addresses.

After that the data feed needs to be correctly set up via the administrator terminal:

![TCNewsFeeder](images/data_feeds_server_tc.png)

The following parameters should be specified on the ["Common" (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — TCNewsFeeder;
  * Feed server — address of the FTP server of Trading Central an a port to connect to it (separated by a colon). The data feed also supports connection via secure SFTP protocol. If you wish to use it, specify the protocol in the address, for example: sftp://sftp.tradingcentral.com. The connection address and the used protocol are determined by agreement with Trading Central.
  * Feed login — login to authorize on the server;
  * Password — password for the authorization.



> For the data feed to work, one should allow ports 20 and 21 on the computer where it is installed. They are necessary to work with FTP server.

After you connect to the FTP server, the data feed starts downloading all available data. After the data re received, it removes them from the FTP server. Further connections to the server are established once in five minutes for checking and downloading new data.

Analytical information that comes from the data feed consists of several elements: the news body with a chart, signals on indicators and signals on Japanese candlesticks. The latter two elements are released not so often as news, so they are inserted only if necessary.

If the data feed operation is terminated, news can be received without the signals for some time, because the earlier signals have been deleted upon receipt already, while new haven't been received yet. While the data feed is operating, it keeps the last four signals in its memory, and inserts them to corresponding news on currency pairs.

![Parameters](images/data_feeds_parameters_tcn.png)

The data feed features the following additional [parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters):

  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * News Request Period — the period of checking and downloading new information in seconds.



```

---

<a id='data-feeds-uninewsfeeder-md'></a>
### 119. `Data-Feeds/UniNewsFeeder.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / UniNewsFeeder

[Previous](Claws-&-Horns-Feeder.md) | [Next](Alliance-News-Feeder.md)

# UniNewsFeeder

UinNewsFeeder is a universal news feed applying the new UniNews protocol.

MetaQuotes Software Corp. has developed its own binary news transfer protocol allowing for high speed of broadcasting news to the MetaTrader 4/5 platforms. Further on, it will allow using news in algorithmic trading by accessing them via MQL5 and the strategy tester.

The new protocol will be of interest to news providers since the integration is completely ready on the side of all MetaTrader 4/5 brokers. The free UinNewsFeeder data feed is able to receive news from any source supporting the new protocol.

## Operation principles

UniNewsFeeder connects to the news provider server and requests news using keywords in multiple languages. First, the data feed receives news missed during its inactivity. After that, the news arrive in real time.

## Setup

Add the new UniNewsFeeder data feed configuration via [the corresponding section of](../../Platform-Setup/Data-Feeds.md) the MetaTrader 5 Administrator:

![UniNewsFeeder setup](images/uninewsfeeder_common.png)

The following parameters should be specified on the [Common (#common)](../../Platform-Setup/Data-Feeds/Configuration-of.md#common) tab of the data feed:

  * Module — UniNewsFeeder64.
  * Feed server — news provider server address.
  * Login — login for connecting to the news provider's server.
  * Password — password for connecting to the news provider's server.



> Connection data is provided by a news provider.

Set the news language and keywords for sorting the news on the [Parameters (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab.

![UniNewsFeeder parameters](images/uninewsfeeder_param.png)

Set the incoming news language in the Languages parameter. The list of languages, in which you want to receive news, is comma-separated. For example, "russian,english,italian". The default value is "any". In this case, the data feed receives news in all languages in the MetaTrader 5 platform. Ask your news provider for the list of available languages.

In the Keywords parameter, set the keywords to be used by the data feed to request news. The default value is "any" (no filtration). Each news provider can sort out news using keywords. Ask your news provider for the list of keywords.

On the ["Parameters" (#parameters)](../../Platform-Setup/Data-Feeds/Configuration-of.md#parameters) tab, you can also use an additional parameter "News Category" — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).

The client terminals will start receiving news right after enabling the data feed. The data feed [journal](../../Platform-Setup/Data-Feeds/Journal-of.md) can be requested to check its operation.

```

---

<a id='data-feeds-universal-dde-connector-md'></a>
### 119. `Data-Feeds/Universal-DDE-Connector.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Data Feeds](../Data-Feeds.md) / Universal DDE Connector

[Previous](Remote-Datafeed.md) | [Next](Universal-DDE-Connector/Installation-and-Setup.md)

# Universal DDE Connector

Universal DDE Connector is a universal gateway that works through protocol DDE (Dynamic Data Exchange). It is used as an intermediary server that accepts quotes from different data sources and passes them to data feed [MetaTrader 5 UniFeeder](MetaTrader-5-UniFeeder.md). Thus, using these two components, you can receive quotes from any data source that supports the DDE protocol.

UniDDE can process up to 1024 financial symbols and distribute quotes to the unlimited number of data feeds [MetaTrader 5 UniFeeder](MetaTrader-5-UniFeeder.md) tuned to it.

This section describes the following aspects of work with UniDDE:

  * Installation and set up of data transmission to the MetaTrader 5 server;
  * Set up of symbols for receiving quotes;
  * Filtering of quotes.



```

---

<a id='data-feeds-universal-dde-connector-filtration-of-quotes-md'></a>
### 119. `Data-Feeds/Universal-DDE-Connector/Filtration-of-Quotes.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Data Feeds](../../Data-Feeds.md) / [Universal DDE Connector](../Universal-DDE-Connector.md) / Filtration of Quotes

[Previous](Setting-Up-Symbols.md) | [Next](UniFeeder-Protocol.md)

<a id="filtration-of-quotes"></a>
# Filtration of Quotes (#filtration-of-quotes)

Universal DDE Connector has the built-in system of automatic filtration of received quotes before they are passed to the [history server](../../History-Server.md). The filtration system consists of several components:

<a id="selecting-the-best-banks"></a>
## Selecting the Best Banks (#selecting-the-best-banks)

One of the most effective ways of cleaning quotes is the automatic selection of the best [banks (#bank)](Setting-Up-Symbols.md#bank) based on statistic data on them. If you tick off "Auto" for the list of banks, UniDDE will start collecting statistics of symbol quotes from banks. Based on this statistics, once a day (except for holidays) several best banks are selected and automatically added to the ["List of banks" (#bank-list)](Setting-Up-Symbols.md#bank-list). Next day filtering of quotes will be performed according to this list. If the selected list of banks is satisfying, you can disable Auto.

> The automatic selection of the list of banks according to the collected results is performed once a day. I.e. the list will be empty the first day.

<a id="white-noise"></a>
## Cleaning from "White" Noise (#white-noise)

For a milder cleaning of the quotes thread from the "white" noise, another new adaptive filtration mechanism is used — ["Automatic filter" (#automatic-filter)](Setting-Up-Symbols.md#automatic-filter). It analyzes the average deviation of received prices and sifts away questionable quotes that fit several template situations.

Very often the thread filtration requires analysis of the next quote for making a decision about the previous questionable price, which may slow down data delivery. But the automatic filter in UniDDE does not allow questionable prices stay longer than half a second. This condition can let some questionable quotes in, but there is one more filtration level described below.

<a id="auto-limit"></a>
## Rough Protection (#auto-limit)

For a rough protection from erroneous price substitution from other symbols the ["Auto Limit" (#auto-limit)](Setting-Up-Symbols.md#auto-limit) mode is used, which doesn't let in new prices if they differ from previous ones by more than the specified number of percents.

```

---

<a id='data-feeds-universal-dde-connector-installation-and-setup-md'></a>
### 119. `Data-Feeds/Universal-DDE-Connector/Installation-and-Setup.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Data Feeds](../../Data-Feeds.md) / [Universal DDE Connector](../Universal-DDE-Connector.md) / Installation and Setup

[Previous](../Universal-DDE-Connector.md) | [Next](Setting-Up-Symbols.md)

<a id="installing-and-setting-up"></a>
# Installing and Setting Up (#installing-and-setting-up)

In order to start installing the Universal DDE Connector, download it from the [technical support website](https://support.metaquotes.net/spfiles/datafeeds/uniddesetup9.exe "Download UniDDE") of MetaQuotes Software Corp. After that start the executable file and perform the simple installation procedure. As soon as the installation is over, start UniDDE.

To prepare UniDDE for connecting MetaTrader5UniFeeder to it, a some configurations are required.

> After you set up UniDDE, you'll need to [set up symbols](Setting-Up-Symbols.md) for translating quotes.

![Universal DDE Connector](images/unidde.png)

<a id="account"></a>
## Account Setup (#account)

During the program installation, one account for accessing from a local computer is created. To enable connection of MetaTrader5UniFeeder to UniDDE an account must be opened - execute the "Add" command in the context menu of the accounts block:

![Accounts](images/unidde_accounts.png)

After you press it, a new line will appear, where you should enter the following data:

  * Login — login for access;
  * Password — password for access;
  * IP Access List — list of allowed IP addresses, separated by commas. Connection using the above specified login and password will be possible only from the specified IP addresses.



Date and time of the last access to UniDDE from a specified account is displayed in column "Last Access".

> To provide higher security, besides accounts with the allowed IP addresses, UniDDE provides the permanent control of all connections with automatic blocking to prevent DoS attacks. In real-time mode, all network connections are analyzed, and if a non-standard activity is detected. the IP address is automatically closed for 5 minites.

<a id="port"></a>
## Setup of Connection Port (#port)

Port specification is also required for connecting MetaTrader5UniFeeder. By default port 2222 is used, but you can change it in field "Server port".

> The specified port must be open on the server where UniDDE is installed.

<a id="setup-of-tick-storage"></a>
## Setup of Tick Storage (#setup-of-tick-storage)

Universal DDE Connector allows storing tick data received from data sources. To do it, tick off field "Save Ticks History". Tick data are saved in file universalddeconnector.ticks, which is located in the UniDDE installation directory.

> When selecting the option of saving of tick data, you should watch the file size they are stored in. If ticks are saved for a long time period and for a great number of symbols, the file size can reach tens of gigabytes.

<a id="journal"></a>
## Journal (#journal)

Results of connecting to a quotes feeder or of the connection of MetaTrader5UniFeeder, as well as other important messages about the operation of UniDDE are reflected in the journal. To open it, press "Journal". All messages are displayed as a table with the following fields:

  * Time — date and time of message creation;
  * IP — IP address the message is connected with. For example, the IP address of MetaTrader5UniFeeder when it is connected to UniDDE;
  * Message — text of the message.



```

---

<a id='data-feeds-universal-dde-connector-setting-up-symbols-md'></a>
### 119. `Data-Feeds/Universal-DDE-Connector/Setting-Up-Symbols.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Data Feeds](../../Data-Feeds.md) / [Universal DDE Connector](../Universal-DDE-Connector.md) / Setting Up Symbols

[Previous](Installation-and-Setup.md) | [Next](Filtration-of-Quotes.md)

# Setting Up Symbols

Universal DDE Connector uses the standard DDE protocol (Dynamic Data Exchange) for accepting quotes from any data source that supports this protocol. During installation of UniDDE, a set of symbols is created, which are configured for receiving quotes from the MetaTrader 4 client terminal. In order to start translating quotes from a client terminal, start it and enable option "Allow DDE Server".

  * Adding a symbol  
In order to add a new symbol, enter its name in field "New Symbol", and then press "Add".
  * Editing a symbol  
In order to change symbol settings, click twice on it in the list or execute the "Edit" command of the context menu.
  * Deleting a symbol  
In order to delete a symbol, select it in the list and press "Delete" or execute the same command of the context menu.



> After adding a symbol, restart UniDDE. Close it using the command of its context menu called by a right click on the icon in the area of notifications. Closing of the UniDDE window does not stop its running, and only minimizes it to the area of notifications.

## Symbol Setup

When adding or editing a symbol, a window of its setting appears:

![Symbol settings](images/unidde_symbol.png)

Settings in this window are divided into several blocks:

### Common parameters

  * Symbol — name of the symbol in Latin letters up to 15 symbols long. A [symbol](../../../Platform-Setup/Symbols.md) of the same name must be created on the MetaTrader 5 server. The symbol name should not necessarily be the same as the symbol name on the data source;
  * Digits — the number of decimal places. The parameter value must be the same as the [analogous symbol parameter (#digits)](../../../Platform-Setup/Symbols/Symbol-Settings/Common.md#digits) on the MetaTrader 5 server;
  * Spread — automatically set spread. Setup of this option is possible only if one price Bid or Ask is received;
  * Force Precision — force transformation of prices like 12345 to 1.2345 if data are received without a separator.



> [A symbol](../../../Platform-Setup/Symbols.md) with exactly the same name must be created on the MetaTrader 5 server.

### DDE Link

In this block parameters of quote receiving from a supplier are configured.

  * Server — name of the source server in the DDE protocol. The most popular data sources can be selected from the list here. Other symbol settings corresponding to it will be set up automatically.
  * Bid topic, Bid item — settings for receiving Bid prices;
  * Ask topic, Ask item, Use — settings for receiving Ask prices. In the "Use" field you can enable/disable direct collection of these data. In this case the Ask price will be calculated automatically based on the value specified in field "Spread";
  * Volume topic, Volume item, Use — parameters for receiving the Ask price. In the "Use" field you can enable/disable direct collection of these data;
  * Bank topic, Bank item, Use — parameters for receiving information about the bank that issued the prices. In the "Use" field you can enable/disable direct collection of these data;
  * List of banks — the list of banks, from which quotes are allowed (separated by commas). Tick off "Auto" to enable the automatic bank selection mode. The auto-selection of banks is described in the section about [filtration](Filtration-of-Quotes.md).



  * Data receiving parameters are set up automatically is you select a server of one of suppliers in the "Server" filed.
  * Contact the supplier for parameters of data receipt.
  * Often, for futures instruments the Last price (price of the last executed deal) is translated. In this case symbols in UniDDE are configured manually so that the Last price is translated as Bid, and Ask is calculated based on tis price and spread settings.

  
---  
  
### Filtration

Filtration parameters for received quotes is set up here.

  * Auto limit — value of the [maximally allowed deviation (#auto-limit)](Filtration-of-Quotes.md#auto-limit) of a new price from the previous one in percents. If the difference between the new price and the previous one exceeds the specified limit, the new price is filtered away (is not passed to the server). This allows to prevent the accidental price substitution for different symbols (for example : USDJPY instead of USDCHF);
  * Automatic filter — enable/disable the automatically adjustable quote filtration. This mode is described in the section devoted to [filtration (#white-noise)](Filtration-of-Quotes.md#white-noise).
  * Accept bid/ask independently — by default, quotes are sent to clients (MetaTrader5UniFeeder) only if Bid has changed. The change of Ask is preserved in such a case, but quotes are not sent to client connection until Bid is updated. This tick allows to disable this behavior and translate new prices when Ask is updated.
  * Use specific time session — use separate time periods. If this option is enabled, fields "Session from" and "To" become active. There you can set time limits for translating symbol quotes.



> Option "Accept bid/ask independently" cannot be enabled for Forex symbols. Quotes where only Ask has changed are considered incorrect and are filtered out by the server. This can create additional load.

## Applying Profiles

A number of ready parameters for receiving quotes from different data feeders are available in UniDDE. To quickly switch between providers, you can use the special command "Apply template..." in the context menu of the symbols list.

![Parameters templates](images/unidde_templates.png)

Select here a necessary quote provider. To save the current set of symbols and their parameters, press "Save symbols...".

  * When you change the provider, parameters of all symbols in the list are changed. So be careful using this procedure. In some systems, parameters of symbols may differ, and some of them can stop working when you change the provider.
  * Each time you change provider, a backup copy of the previous state (file with SYM extension) is created in the "backup" folder located in the UniDDE installation directory. To restore the list of symbols, only use command "Load symbols..." and specify a required file.

  
---

```

---

<a id='data-feeds-universal-dde-connector-unifeeder-protocol-md'></a>
### 119. `Data-Feeds/Universal-DDE-Connector/UniFeeder-Protocol.md`

```markdown
[🏠 Document Start](../../../../README.md) / [MetaTrader 5 Trading Platform](../../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../../Platform-Components.md) / [Data Feeds](../../Data-Feeds.md) / [Universal DDE Connector](../Universal-DDE-Connector.md) / UniFeeder Protocol

[Previous](Filtration-of-Quotes.md) | [Next](../../Gateways.md)

# UniFeeder Protocol

The general features of the UniFeeder protocol are provided below to help you understand its operation principles.

  * The data feed establishes TCP connections with a data source.
  * The data feed reads the data line by line. The "\r\n" sequence serves as a line separator.
  * Authorization:
    * After connection is established, the data feed waits for a login request from the data source. The line containing "Login: " is expected, for example, "Login :\n\r". The "waiting login request" entry appears in the Journal while waiting for the request.
    * After the request is received, the "login request received" entry appears in the Journal, and the data feed sends the line with the login to the data source, for example, "user_test\r\n".
    * The data feed waits for the password request from the data source. The line containing "Password: " is expected. The "login sent [%S], waiting password request" entry appears in the Journal while waiting for the request.
    * After the request is received, the "password request received" entry appears in the Journal, and the data feed sends the line with the password to the data source, for example, "password\r\n".
    * The data feed waits for the notification of successful authorization. The line containing "Access granted" is expected. The "password sent, waiting access confirmation" entry appears in the Journal while waiting for the request.
    * After receiving the notification, the "Login: '%S' successful" entry appears in the Journal.
    * The data feed sends the line containing the symbols, for which it is allowed to send quotes. The line looks as follows "> Symbols:USDRUB,EURUSD,EURRUB\r\n".
    * The data feed switches to the data receipt mode (quotes and news).
  * Data receipt:
    * The data feed reads the data line by line. The "\r\n" serves as a line separator.
    * The lines beginning with ">" or "<" reserved characters are skipped, except for the lines beginning with "< News".
    * If the "< News\r\n" line is received, the data feed switches to news receipt mode:
      * After the "< News\r\n" line, the data feed reads the NewsTopic structure (read MetaTrader 4 API documentation for more details).
      * Next, the data feed reads the news body. The size of the news body is set in bytes in the NewsTopic::len field.
      * After reading the body, the news is sent to the platform, while the data feed continues the data receipt.
    * If the line does not begin with "<" or ">", it is deemed to be a tick line.
      * The tick line format: "<Symbol name> <bid> <ask>\r\n". Example: "USDJPY 1.0106 1.0099\r\n".
      * If bid or ask is less than zero, or bid exceeds ask, the tick is skipped and the "failed to parse tick, invalid bid/ask" entry appears in the Journal.



Below is an example of the network exchange dump. The data sent by the data feed is shown in red:
    
    
    Welcome
    Login: test_user
    Password: test_password
    Access granted
    USDJPY 0 4.0000 19.0000
    GBPUSD 0 8.0000 19.0000
    USDCHF 0 15.0000 16.0000
    USDCHF 0 6.0000 25.0000
    USDJPY 0 6.0000 17.0000
    GBPUSD 0 6.0000 21.0000
    USDCHF 0 7.0000 24.0000
    USDJPY 0 9.0000 14.0000
    GBPUSD 0 9.0000 18.0000
    USDCHF 0 9.0000 22.0000
    USDJPY 0 5.0000 18.0000
    GBPUSD 0 4.0000 23.0000
    USDCHF 0 7.0000 24.0000
    USDJPY 0 7.0000 16.0000
    GBPUSD 0 13.0000 14.0000

```

---

<a id='gateways-borsa-istanbul-md'></a>
### 119. `Gateways/Borsa-Istanbul.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / Borsa Istanbul

[Previous](FXCM-PRO.md) | [Next](Interactive-Brokers.md)

<a id="metatrader-5-gateway-to-borsa-istanbul-futures"></a>
# MetaTrader 5 Gateway to Borsa Istanbul Futures (#metatrader-5-gateway-to-borsa-istanbul-futures)

[Borsa İstanbul](https://borsaistanbul.com/) brings together all exchanges operating in the Turkish capital markets under a single roof. Established on the basis of Capital Markets Law no. 6362, Borsa İstanbul is an internal entity under private law. Borsa İstanbul is a self-regulatory entity.

Borsa İstanbul offers the opportunity to invest in various products in an organized, transparent and reliable trading environment to local and international investors with its modern technological capabilities. On all markets of Borsa İstanbul, transactions are conducted electronically, and market information is disseminated on a real-time basis.

Borsa İstanbul markets are organized under five main categories: Equity Market, Emerging Companies Market, Debt Securities Market, Foreign Securities Market and Futures and Options Market.

MetaTrader 5 Gateway to Borsa Istanbul Futures allows futures trading at the Main Board of [Futures and Options Market](https://borsaistanbul.com/en/products-and-markets/markets/futures-and-options-market) at [Borsa Istanbul](https://borsaistanbul.com/):

  * Equity Futures (Main Board)
  * Equity Index Futures (Main Board)
  * Currency Futures (Main Board)
  * Precious Metals Futures (Main Board)
  * Commodity Futures (Main Board)
  * Power Futures (Main Board)



> [Request MetaTrader 5 Gateway to Borsa Istanbul Futures](https://support.metaquotes.net/en/market/product/282)

<a id="preparing-for-the-gateway-launch"></a>
## Preparing for the Gateway Launch (#preparing-for-the-gateway-launch)

Before setting a brokerage company gateway, configure the virtual network channel to be able to connect to Borsa Istanbul servers.

Configuration of a virtual network channel is performed together with Borsa Istanbul technical specialists. To create a virtual channel to the exchange, a broker must request technical requirements and recommendations for connection to the Borsa Istanbul virtual private network (VPN) from the mercantile exchange technical support team. At the next stage the mercantile exchange technical support team will submit to the brokerage company description of the equipment settings on SMX side: tunnel type, data encryption method, data encryption keys etc.

The programmed virtual channel can be created for connection to Borsa Istanbul test environment.

<a id="how-the-gateway-works"></a>
## How the Gateway works (#how-the-gateway-works)

MetaTrader 5 Gateway to Borsa Istanbul Futures is a separate BorsaIstanbulVIOPGateway64.exe module that uses the MetaTrader 5 Gateway API. The gateway operates over 5 FIX channels. One FIX connection is used for passing Reference Data (symbol settings), two more are used for trading and the other two for receiving data on trades performed via other trading systems (Drop Copy). Some symbols are processed on the one and Drop Copy connection, the rest symbols are handled on the other one. Information about what servers process specified symbols is transmitted via the Reference Data channel.

Orders and positions are synchronized over the SOAP service, and quotes are delivered via a TIP channel.

Orders are sent to the MetaTrader 5 Gateway to Borsa Istanbul for processing in accordance with configured [routing rules (#routing)](Borsa-Istanbul.md#routing). Processing of requests depends on the type of the order:

Order Type | Execution  
---|---  
Market Orders | Delivered directly to the exchange as a market order.  
Buy Limit Sell Limit | Delivered directly to the exchange as limit orders.  
Buy Stop Sell Stop | Delivered directly to the exchange as stop orders.  
Buy Stop Limit Sell Stop Limit | Delivered directly to the exchange as stop limit orders.  
Take Profit Stop Loss | Processed on the MetaTrader 5 side. After activation in the MetaTrader 5 terminal, a market order to close a client's position is sent to the exchange.  
Stop Out | Processed on the MetaTrader 5 side. In case a limit order must be removed after a Stop out level has been reached, an appropriate request for its removal is sent to Borsa Istanbul server. In case a position must be closed because of Stop out, a market request to close a client's position is sent to the exchange.  
  
The below diagram shows the interaction of the gateway with the exchange (the exchange time UTC+3 is specified):

![MetaTrader 5 and Gateway interaction scheme](images/borsa_scheme.png)

  * The gateway starts to connect to FIX servers of the exchange at 4:30 . It will try to obtain from the exchange actual files with risk parameters till 22:30. When new files appear, the gateway downloads them and updates symbol settings in MetaTrader 5.
  * Clients' balances are synchronized with the exchange at 9:00by default. This time can be changed using the BalancesSyncTime parameter.
  * The trading session lasts from 9:30 to 18:30.
  * The exchange updates official exchange rates at 15:30. These rates are used to recalculate the value of contracts that are not expressed in Turkish liras: the symbol's tick value is calculated and set based on these rates. New rates are not applied until the end of the trading session (previous rates are used).
  * During the time specified in the [EOD Time (#eod-time)](Borsa-Istanbul.md#eod-time) parameter, the gateway downloads new rates from the exchange and recalculates results of all trades executed during this session using the new rates.
  * Immediately after this, the gateway receives the EOD file from the exchange. Results of all trades executed from 15:30 until the end of the session are recalculated using new currency rates. Update of risk parameters of instruments, as well as of inter-month and inter-contract [spreads](../../Platform-Setup/Spreads.md), calculation of variation margin, delivery (closing of positions of expired futures) and unblocking of accumulated profits are performed based on the EOD file.
  * If PositionsSync parameter is enabled, positions are synchronized at 19:01 (after applying the EOD file).
  * At 22:30, the gateway is disconnected from the exchange's FIX servers.



<a id="settings"></a>
## Configuring the gateway (#settings)

To start working, add [a new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway settings](images/borsa_common.png)

Set the following parameters on the "Common" tab:

  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Module — specify BorsaIstanbulVIOPGateway64 and accept the default settings after the module selection.
  * Trading server — IP address and the port of the exchange's first FIX server, where trade requests are processed.
  * Trading login — a login for connection to the first trade server of the exchange. Corresponds to the UserName (553) tag in the FIX protocol.
  * Password — a password for connection to the first trade server of the exchange. Corresponding to the Password tag (554) in FIX protocol. The exchange requires that the password used for connection be changed every 90 days. The gateway automates this process by changing the password in advance, every 70 days, in case of unforeseen issues. To activate this feature, change the password manually once. This action will provide the gateway with the last password change date, from which further tracking will be performed.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * Connection details are provided by the exchange.

  
---  
  
Now, go to the "Parameters" tab.

![Gateway parameters setup](images/borsa_param.png)

Specify the following parameters values here:

  * FIX Trade SenderCompID — a standard parameter of the FIX messages header used for a data sender identification. This parameter is provided by the exchange as the value of SenderCompID (49).
  * FIX Trade TargetCompID — a standard parameter of the FIX messages header used for trading messages recipient identification. This parameter is provided by the exchange as the value of TargetCompID (56).
  * FIX Trade SenderSubID — FIX messages header standard parameter used for a trading participant (a legal entity) identification. This parameter is provided by the exchange as the value of SenderSubID.
  * FIX Trade Second Address — IP address and the port of the exchange's second FIX server, where trade requests are processed.
  * FIX Trade Second Login — a login for connection to the second trade server of the exchange. Corresponds to the UserName (553) tag in the FIX protocol.
  * FIX Trade Second Password — a password for connection to the second trade server of the exchange. Corresponding to the Password tag (554) in FIX protocol.
  * FIX Trade Second SenderCompID — a standard parameter of the FIX messages header used for a data sender identification. This parameter is provided by the exchange as the value of SenderCompID (49).
  * FIX Trade Second TargetCompID — a standard parameter of the FIX messages header used for trading messages recipient identification. This parameter is provided by the exchange as the value of TargetCompID (56).
  * FIX Trade Second SenderSubID — FIX messages header standard parameter used for a trading participant (a legal entity) identification. This parameter is provided by the exchange as the value of SenderSubID.
  * FIX Drop Copy Address — the IP and port of the first Drop Copy server. Operations performed via other trading systems are processed on this FIX server.
  * FIX Drop Copy Login — login for connection to the first Drop Copy server of the exchange. Corresponds to the UserName (553) tag in the FIX protocol.
  * FIX Drop Copy Password — password for connection to the first Drop Copy server of the exchange. Corresponding to the Password tag (554) in FIX protocol.
  * FIX Drop Copy SenderCompID — a standard parameter for the FIX message header, which is used for identifying a data sender in the Drop Copy service. This parameter is provided by the exchange as the value of SenderCompID (49).
  * FIX Drop Copy TargetCompID — a standard parameter for the FIX message header, which is used for identifying a message recipient in the Drop Copy service. This parameter is provided by the exchange as the value of TargetCompID (56).
  * FIX Drop Copy SenderSubID — a standard parameter for the FIX messages header, which is used for a trading participant (a legal entity) identification in the Drop Copy service. This parameter is provided by the exchange as the value of SenderSubID.
  * FIX Drop Copy Third Address — IP-address and port of the third Drop Copy server. This is the exchange's FIX server which processes operations executed through other trading systems.
  * FIX Drop Copy Third Login — login for connection to the exchange's third Drop Copy server. Corresponds to the UserName tag (553) in the FIX protocol.
  * FIX Drop Copy Third Password — password for connection to the exchange's third Drop Copy server. Corresponds to the Password tag (554) in the FIX protocol.
  * FIX Drop Copy Third SenderCompID — standard FIX message header parameter which is used to identify the trading data sender. This parameter is provided by the exchange as the SenderCompId (49) value.
  * FIX Drop Copy Third TargetCompID — standard FIX message header parameter which is used to identify the recipient of trading messages. This parameter is provided by the exchange as the TargetCompId (56) value.
  * FIX Drop Copy Third SenderSubID — standard FIX message header parameter which is used to identify a trading participant (legal entity). This parameter is provided by the exchange as the SenderSubId value.
  * FIX Drop Copy Fourth * — a set of parameters for the fourth Drop Copy server: Address, Login, Password, SenderCompID, TargetCompID and SenderSubID. They are set similarly to the third server parameters.
  * FIX Drop Copy Fifth * — a set of parameters for the fifth Drop Copy server: Address, Login, Password, SenderCompID, TargetCompID and SenderSubID. They are set similarly to the third server parameters.
  * FIX Drop Copy Sixth * — a set of parameters for the sixth Drop Copy server: Address, Login, Password, SenderCompID, TargetCompID and SenderSubID. They are set similarly to the third server parameters.
  * FIX Reference Data Address — IP address and port of the exchange's FIX server, through which trade symbol settings are transmitted (the Reference Data server).
  * FIX Reference Data Login — login for connection to the Reference Data server. Corresponds to the UserName (553) tag in the FIX protocol.
  * FIX Reference Data Password — password for connection to the Reference Data server. Corresponding to the Password tag (554) in FIX protocol.
  * FIX Reference Data SenderCompID — a standard parameter for the FIX message header, which is used for identifying a data sender in the Reference Data service. This parameter is provided by the exchange as the value of SenderCompID (49).
  * FIX Reference Data TargetCompID — a standard parameter for the FIX message header, which is used for identifying a message recipient in the Reference Data service. This parameter is provided by the exchange as the value of TargetCompID (56).
  * FIX Reference Data SenderSubID — a standard parameter for the FIX messages header, which is used for a trading participant (a legal entity) identification in the Reference Data service. This parameter is provided by the exchange as the value of SenderSubID.


  * FIX Reference Data Detached — by default, when any of the FIX connections is interrupted, the gateway completely disconnects from the exchange to avoid data integrity violation. The settings of trading instruments transmitted through the FIX Reference channel are updated not very often. Therefore, in some cases, the loss of this connection can be disregarded. To prevent the gateway from disconnecting from the exchange upon losing the FIX Reference Data connection, set "FIX Reference Data Detached" to "No".


  * FIX Connect Attempts — the maximum number of attempts to connect to the current IP address of the FIX channel (Trade, Drop Copy, or Reference). The default value is three. After the specified number of unsuccessful attempts, the gateway will try to connect to the next address.


  * FIX Trade SMPLevel — value of tag 21114 in the FIX protocol. Possible values: 'Within' (default) and 'Across'. The value is used along with FIX Trade SMPMethod and FIX Trade SMPID for [Self-Match Prevention Feature](https://borsaistanbul.com/files/self-match-prevention-smp-feature-technical-functionality-principles.pdf), an algorithm that prevents the matching of orders of the same client. Please contact the exchange to find out the required parameter values.
  * FIX Trade SMPMethod — value of tag 21115 in the FIX protocol. Possible values: Aggressive (default), Passive, Both.
  * FIX Trade SMPID — value of tag 21116 in the FIX protocol. If this parameter is not filled, the gateway will not transmit the SMPLevel (21114) and SMPMethod (21115) values.


  * TIP Address — IP address and port of the exchange server, through which quotes are transmitted over the TIP protocol.
  * Nasdaq Identifiers Path — path to the file containing identifiers of instruments in the TIP channel. It is used for the gateway to exchange connection in the middle of the trading session.
  * Nasdaq Identifiers Enabled — enable\disable processing of the file specified in the Nasdaq Identifiers Path parameter. Default is No. At the beginning of the day, the exchange send over the TIP protocol information about symbol identifiers (identifier/symbol name pairs). Further quotes are provided only with an identifier (without a name). To enable the gateway to receive quotes after connecting to Borsa Istanbul in the middle of the trading session, enable this option. The gateway will load the identifiers from the file specified in Nasdaq Identifiers Path.
  * Symbols Path — path for importing the exchange symbols. By default, if this parameter is absent, the gateway imports the exchange's trading symbols to \Preliminary subdirectory with trading ability disabled. A system administrator should manually relocate imported symbols to the proper group and allow trading for them. If this parameter is present, the gateway imports trading symbols following the specified path. The ability to trade the symbols is enabled immediately. Thus, the administrator has no need to additionally configure the symbols. For example, if "BorsaIstanbul" is specified in the parameter, working symbols will be automatically added to the BorsaIstanbul\* subdirectory, and expired symbols will be transferred to BorsaIstanbul\Expired\*.
  * Takas Web Service Address — the address of the server that transmits data for synchronizing client balance positions on the MetaTrader 5 side (the SOAP service).
  * Takas Web Service Login — login for connection to the SOAP service (provide by the Exchange).
  * Takas Web Service Password — password for connection to the SOAP service (provide by the Exchange).
  * Takas Web Service Member Code — trading participant code, which should be specified for connecting to the SOAP service (provide by the Exchange).
  * Genium Risk Parameters Url — the address for downloading files with risk parameters. These files are used for obtaining current settlement prices, for updating risk parameters of instruments, for calculating the variation margin and for updating the inter-month and inter-contract spreads of instruments.
  * Positions Sync — enable\disable synchronization of positions with the SOAP service at the end of the trading session. Enabled by default (set to Yes).
  * Balances Sync — enable\disable synchronization of client balances with the SOAP service at the end of the trading session. Enabled by default (set to Yes).
  * Balances SyncTime — the start time of balance synchronization with SOAP. Synchronization starts at 09:00 by default.
  * Daily Rollover Positions — enable (Yes)\disable (No) rollover operations (charging variation margin) at the end of the trading session. Enabled by default (set to Yes).


  * Settlement Prices File Path — full path to the CSV file with settlement prices. The file must be UTF-8 encoded and prices must be in X,YYY format (for example, 1,234). By default, the path is not specified, and the gateway receives prices from the FIX Reference Data channel or from the 'span' file. If the path is specified, the gateway checks the date when the file was last modified. If the file has been modified on the current day, its contents are read and applied. If the file has not been modified, the gateway will use prices from the FIX Reference Data channel or from the 'span' file. If the file does not contain data for certain instruments, the relevant data will be taken from the FIX Reference Data channel or from the 'span' file.
  * EOD Time — end-of-day time on the exchange. Variation margin operations are performed at this time, and not upon the [receipt of the "EOD span" file (#schedule)](Borsa-Istanbul.md#schedule). The parameter is set as "HH:MM". Valid values are from 18:30 (end of the afternoon session) to 18:59 (beginning of the evening session). The default time is 18:52.


  * Trade Requests Limit — the maximum total number of requests sent to the exchange per second. Default is 0, which means there is no limit.
  * Client Trade Requests Limit — the maximum number of requests per second sent by each separate client to the exchange. Default is 0, which means there is no limit.
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.
  * Stop Out Allow — allow closing of positions upon reaching [Stop Out (#stopout)](../../Platform-Setup/Groups/Group-Settings.md#stopout). If set to "No" (default), positions opened via the gateway will not be closed automatically, if Stop Out is reached on the trading platform side. If a position is opened with Stop Out Allow = Yes, then closing by Stop Out can occur even if you change the parameter value to "No". It is only guaranteed that the ban to close will be effective for positions opened after changing the parameter value to "No".



Two addresses are supported for each FIX channel: primary and secondary. You can specify them separating by commas. For example: FIX Drop Copy Address = 31.145.34.115:30187,31.145.34.115:10030. If the gateway fails to connect to the first address, it will automatically switch to the second one.

The gateway supports the old and new exchange environments: BISTECH 2 and BIST 3.0, respectively. The parameters below are only used to connect to the old environment. If they are filled, the following parameter groups will be ignored: FIX Drop Copy Third *, FIX Drop Copy Fourth *, FIX Drop Copy Fifth * and FIX Drop Copy Sixth *.

  * FIX Drop Copy Second Address — IP address and port of the second Drop Copy sever. This is the exchange's FIX server which processes operations executed through other trading systems.
  * FIX Drop Copy Second Login — login for connection to the exchange's second Drop Copy server. Corresponds to the UserName tag (553) in the FIX protocol.
  * FIX Drop Copy Second Password — password for connection to the exchange's second Drop Copy server. Corresponds to the Password tag (554) in the FIX protocol.
  * FIX Drop Copy Second SenderCompID — standard FIX message header parameter which is used to identify the trading data sender. This parameter is provided by the exchange as the SenderCompId (49) value.
  * FIX Drop Copy Second TargetCompID — standard FIX message header parameter, which is used to identify the recipient of trading messages. This parameter is provided by the exchange as the TargetCompId (56) value.
  * FIX Drop Copy Second SenderSubID — standard FIX message header parameter which is used to identify a trading participant (legal entity). This parameter is provided by the exchange as the SenderSubId value.



The next stage is to specify the groups of clients, whose requests will be processed via the MetaTrader 5 Gateway to Borsa Istanbul, as well as symbols, by which the gateway processes trading operations and broadcasts quotes.

![Configuring groups and symbols](images/borsa_groups_symbols.png)

Make sure to enable the "Allow importing symbol settings" option. The gateway imports symbols from the exchange to the MetaTrader 5 platform in accordance with the [Symbols Path (#symbolspath)](Borsa-Istanbul.md#symbolspath) parameter and further controls parameters of these symbols.

> The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

<a id="groups-configuration-and-using-profitloss-for-the-current-trading-session"></a>
## Groups Configuration and Using Profit/Loss for the Current Trading Session (#groups-configuration-and-using-profitloss-for-the-current-trading-session)

According to the exchange rules, profit obtained during a trading day cannot be used before clearing is performed. In fact, only clearing determines the financial results of all transactions during the day. The profit received by a client during the current trading session is accumulated during the trading session and released only after the clearing becoming available for use by the client for further trade.

In order to avoid a situation in which a client who suffered losses will try to continue trading, fixed loss is withdrawn immediately.

In this regard, the following parameters should be specified in "Profit/loss in free margin" block of Margin tab in the settings of the group that will operate at Borsa Istanbul:

![Group configuration](images/borsa_margin.png)

All financial accounting on Borsa Istanbul is done in Turkish liras. Thus, Turkish liras (TRY) should be specified as deposit currency in the group settings:

![Group configuration](images/borsa_group_common.png)

<a id="routing"></a>
## Configuring Trade Requests Routing (#routing)

Configure the routing to let the clients requests to be transmitted to the Borsa Istanbul Futures gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

In the screenshots below all orders created by users in the real\borsa\* groups by symbols from the BorsaInstanbul\* section will be sent to the gateway for processing.

![Configuring Trade Requests Routing](images/borsa_routing.png)

<a id="configuring-trading-accounts"></a>
## Configuring Trading Accounts (#configuring-trading-accounts)

Each client on MetaTrader 5 side should be provided with a corresponding separate trading account on the exchange. After an account is opened at the exchange, it should be connected with the account within the platform. Open the appropriate client account and move to Account tab:

![Configuring Trading Accounts](images/borsa_account.png)

A new entry should be added in "Trade accounts" section. Select MetaTrader 5 Gateway to Borsa Istanbul in Gateway ID field. Specify the Borsa Istanbul client account in "Account" field.

<a id="gateway-launch"></a>
## Gateway Launch (#gateway-launch)

After the application of all settings described above, your gateway is almost ready to go. It will connect to Borsa Istanbul server.

Borsa Istanbul submits a default password for the first connection (specified in the [Trading Password (#password)](Borsa-Istanbul.md#password) field). Borsa Istanbul security policy requires the password to be changed right after the first connection. The gateway automatically generates and installs the new password. You can [change the password (#change-password)](Borsa-Istanbul.md#change-password) later.

The password should meet Borsa Istanbul safety requirements:

  * the password should consist of 8 characters;
  * the password should contain 3 types of symbols: lowercase Latin characters (a-z), upper case ones (A-Z), numbers (0-9);
  * the password must be different from the previous ones (last 6 used passwords are checked).



The following entries appear in the gateway journal when the password is changed automatically:

12:23:48 Gateway new password has generated due to previous logon response  
---  
  
The following entry means that the gateway has successfully connected to Borsa Istanbul and is now ready for operation:

12:24:19 Gateway synchronized with Borsa Istanbul exchange  
---  
  
In case of connection failure, the entries concerning the failure reasons appear in the gateway journal.

New symbols are imported after the first connection. As noted above, after adding new symbols, trading should be enabled for them. After that the MetaTrader 5 platform main trade server must be restarted. These actions should be performed only during the gateway first launch.

After the main trading server is restarted, the gateway installation and configuration is complete. Traders can perform transactions on Borsa Istanbul using their MetaTrader 5 client terminal.

<a id="updating-the-symbols-settings"></a>
## Updating the Symbols Settings (#updating-the-symbols-settings)

The gateway automatically updates the symbols settings during its operation, if necessary. Appropriate entries appear in the journal in that case:

12:25:36 SymbolsBase symbol 'F_EURUSD1213S0' config updated  
---  
  
<a id="change-password"></a>
## Changing the Password (#change-password)

In case you need to change the password used by the gateway for connection to Borsa Istanbul server, simply specify the new password in Trading password field. The password must comply with [security requirements (#passwod-security)](Borsa-Istanbul.md#passwod-security). Once the settings are saved, the password at Borsa Istanbul server will be changed automatically.

12:25:48 Gateway password has been changed manually  
---

```

---

<a id='gateways-cboe-fx-md'></a>
### 119. `Gateways/Cboe-FX.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / Cboe FX

[Previous](Euronext-FX.md) | [Next](LMAX-Global.md)

<a id="metatrader-5-cboe-fx-gateway"></a>
# MetaTrader 5 Cboe FX Gateway (#metatrader-5-cboe-fx-gateway)

[Cboe FX](https://fx.cboe.com) is one of the largest ECNs for the institutional FX market. The key advantages of Cboe FX are:

  * independence and transparency
  * complete Market Depth
  * centralized price setting system (defining the best price of all providers)
  * direct and anonymous market access
  * high trade execution speed
  * real-time quotes stream



The following financial assets can be traded via Cboe FX:

  * Currency pairs: 53 basic currency pairs and 13 additional ones.
  * Precious metals: XAGUSD, XAUUSD, LPDUSD, LPTUSD, XPDUSD, XPTUSD.



The MetaTrader 5 Gateway to Cboe FX enables brokers to transmit trading operations from the MetaTrader 5 platform to a ECN system. This will attract many customers who trade via Cboe FX. In addition, the gateway provides the ability for brokerage companies to earn additional income by automatically rearing the prices (spread increase) transmitted from ECN to the platform.

<a id="getting-started-with-cboe-fx"></a>
## Getting started with Cboe FX (#getting-started-with-cboe-fx)

First of all a broker should contact Cboe FX using the specified contact details, and to sign an agreement with them.

For sales inquiries: | Technical support:  
---|---  
Americas: +1 212 209 1420 Europe: +44 (0)20 7131 3450 Asia: +65 6911 6688 fxtradedesk@cboe.com | +1 212 378 8558 fxtradedesk@cboe.com  
  
When this stage is completed, authorization data for connection to ECN will be provided to the brokerage company. Additional information is available on the official Cboe FX website at <https://fx.cboe.com>.

> [Order the MetaTrader 5 Gateway to Cboe FX](https://support.metaquotes.net/en/market/product/262)

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

MetaTrader 5 Gateway to Cboe FX is a separate module that uses the MetaTrader 5 Gateway API for operation. It streams quotes and the Market depth, as well as it transmits clients' trade requests to the Cboe FX ECN system and back.

All orders entered in ECN are transferred to the unified requests database. The system selects appropriate orders automatically executing opposite orders with matching parameters (symbol, price etc.)

The broker's servers are configured in such a way that the clients' market requests are sent to MetaTrader 5 Cboe FX Gateway. The gateway verifies correctness of the client requests. In case validation is successful, the relevant trade request is directed to Cboe FX ECN server via a standard protocol for exchanging financial information - FIX. After receiving a response from the Cboe FX server, the gateway saves the trade request processing result in the platform, which in its turn reports this result to the trader.

Orders will be sent to MetaTrader 5 Cboe FX Gateway for processing in accordance with the configured [routing rules (#routing)](Cboe-FX.md#routing). Processing of requests depends on the type of the order, as well as in the gateway configuration.

Order type | Execution  
---|---  
Market Order | Delivered directly to Cboe FX as a market order.  
Take Profit Buy Limit Sell Limit | Depends on [LimitOrdersCoverage (#parameters)](Cboe-FX.md#parameters): LimitOrdersCoverage=Gateway (default) Limit orders are processed on the side of Cboe FX. Once a limit order has been placed by a client, an appropriate order is sent to Cboe FX. Take Profit orders are processed the same way as in the Limit mode. The Cboe FX system checks the availability of the required amount of funds to cover any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out. Margin reservation of the clients should be configured for the appropriate order types in case Limit orders are directly delivered to an external system. By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client. LimitOrdersCoverage=Limit Limit Orders and Take Profit orders are processed on the side of the MetaTrader 5. Once a limit order is triggered, an equivalent limit order is sent to Cboe FX. That order has a short action time specified in LimitOrdersCoverageTimeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Cboe FX. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5. A limit order with the price equal to a Take Profit level is sent to Cboe FX at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Cboe FX. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on MetaTrader 5 side.   
Limit mode allows to protect against slippage, as a limit order is sent to Cboe FX system with a specified price rather than a market order for execution by the current price. LimitOrdersCoverage=Market Limit orders and Take Profit orders are processed on the MetaTrader 5 platform side. Once they trigger, an appropriate market order us sent to Cboe FX.  
Buy Stop Sell Stop Stop Loss Stop Out | Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to Cboe FX system.  
Buy Stop Limit Sell Stop Limit | Processed on the MetaTrader 5 side. Upon order order activation, an appropriate limit order is created in MetaTrader 5, and this order is then processed in accordance with the value of the LimitOrdersCoverage parameter.  
  
  * Slippages are possible when transmitting market orders to ECN as a result of pending orders activation. The price on the Cboe FX server may change at the moment when the price has reached an order activation level but the market transaction has not yet been performed.
  * Due to the fact that pending orders are not transmitted to ECN, they will not be visible in the Depth of Market.

  
---  
  
<a id="gateway-setup"></a>
## Gateway Setup (#gateway-setup)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Common gateway settings](images/hotspot_common.png)

Set the following parameters on the "Common" tab:

  * Module — Cboe FXGateway64. Agree to set the default settings after selecting the module.
  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Trade server — Cboe FX server IP-address and port, where trade requests are processed. They are designated as "ip" and "port" parameters in "Orders" section in the connection data provided by Cboe FX.
  * Trading login — a login for connection to the Cboe FX server. Designated as "username" parameter in "Orders" section in the connection data provided by Cboe FX.
  * Trading password — a password for connection to the Cboe FX server. Designated as "password" parameter in "Orders" section in the connection data provided by Cboe FX.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The data for connection to the Cboe FX server, where trade requests are processed, is provided with the agreement.

  
---  
  
Other parameters are set similarly to other gateways. Default values are used in most cases.

Now, go to the "Parameters" tab.

![Gateway parameters](images/hotspot_param.png)

Specify the following parameters values here:

  * FIX Trade TargetCompID — standard parameter of FIX messages header used for trading messages recipient identification. This is Cboe FX company identifier in the trade flow.
  * FIX Market Data Address — address and port of the Cboe FX server that streams quotes. They are provided as "ip" and "port" parameters in "Market Data" section in the connection data provided by Cboe FX.
  * FIX Market Data Login — login for connection to the quoting server. Provided as "username" parameter in "Market Data" section in the connection data provided by Cboe FX.
  * FIX Market Data SenderCompID — standard parameter of FIX message header used for the identification of the quote message sender. This is your company identifier in the quote stream.
  * FIX Market Data TargetCompID — standard parameter of FIX message header used for the identification of the quote message recipient. This is the Cboe FX identifier in the quote stream.
  * Limit Orders Coverage Mode — the mode of processing of Limit and Take Profit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:
    * Market — limit and Take Profit orders are processed on the MetaTrader 5 platform side. Once the order triggers, an appropriate market order is sent to Cboe FX.
    * Limit — limit and Take Profit orders are processed on the MetaTrader 5 side.  
  
Once a limit order is triggered, an equivalent limit order is sent to Cboe FX. That order has a short action time specified in Limit Orders Coverage ModeTimeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Cboe FX. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.  
  
A limit order with the price equal to a Take Profit level is sent to Cboe FX at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Cboe FX. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on the MetaTrader 5 side.  
  
The Limit mode allows to protect against slippage, as a limit order is sent to the Cboe FX system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to Cboe FX.
    * Gateway — limit orders are processed on the Cboe FX side. Once a limit order has been placed by a client, an appropriate order is sent to Cboe FX. Take Profit orders are processed the same way as in the Limit mode.
  * Limit Orders Coverage Timeout — expiry of Limit Orders that are sent to Cboe FX in the Limit mode. Specified in seconds. The default value is 5.
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



  * The data for connection to the Cboe FX quote server, as well as identifiers for trading and quoting connection are provided by Cboe FX with the agreement.
  * After editing the market depth settings the main trading server must be restarted to let the changes take effect.
  * The maximum market depth provided by Cboe FX is equal to 11.

  
---  
  
The next stage is to specify the groups of the clients, whose requests will be processed via the MetaTrader 5 Cboe FX Gateway.

![Setup of groups for the gateway to work with](images/hotspot_groups.png)

Then configure the list of symbols, according to which the gateway will process trade operations and feed quotes.

![Configuring the symbols](images/hotspot_symbols.png)

Make sure to enable the option "Allow importing symbol settings", as the gateway adds necessary symbols and changes their settings by itself.

  * The symbols imported by the gateway are put to the "\Preliminary\CboeFX" symbols subgroup. All symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After symbols are transferred and trading is enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case the symbol is not transferred and its trading ability is not turned off.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="routing"></a>
## Configuring trade requests routing (#routing)

Configure the routing to let the clients requests to be transmitted to the Cboe FX gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway. Add the previously created gateway at the Dealers tab.

![Configuring trade requests routing](images/hotspot_routing.png)

After the correct execution of the steps described above, Cboe FX gateway will be ready for use.

<a id="getting-started"></a>
## Getting Started (#getting-started)

After it has been launched, the gateway will connect to the liquidity provider:

  * to receive symbols and the price stream
  * to transmit trade requests and to receive notifications about executed trades



Connection to the liquidity provider is performed via FIX protocol. All incoming and outgoing FIX messages are stored on the disk at the \gateway\Cboe FX\fix\ directory of the history server. The gateway follows the Cboe FX ECN schedule — it will close connection with the ECN after the end of the working session, and will establish the new connection after the beginning of the next session.

The result of the gateway operation is reflected in its [journal](../../Platform-Setup/Gateways/Journal-of.md).

<a id="getting-profit-from-agency-work"></a>
## Getting Profit from Agency Work (#getting-profit-from-agency-work)

The gateway streams prices from the external trading system and [controls symbol settings (#symbols)](Cboe-FX.md#symbols). The standard feature of gateways is the ability to change the quotes and market depth transmitted to the clients from an external system.

The gateway received prices from Cboe FX ECN and transmits them to clients taking into account transformation settings. Clients perform trading operations using converted prices. However, while processing trading operations on the gateway and their transmission to ECN, initial, not converted prices are automatically used.

Thus, by increasing the selling price and reducing the purchase price ("price spreading") a brokerage company receives its profit share from each deal performed at Cboe FX. The correction value is set separately for each symbol on the "Translations" tab:

![Configuring transformations](images/hotspot_translations.png)

Here you can configure matching of symbol names used in Cboe FX with the names used in your MetaTrader 5 platform. For example, if the symbol name in Cboe FX is EURUSDHS, and it is called EURUSD in the MetaTrader 5, enter EURUSD in the "Symbol" field and EURUSDHS in the "Source" field.

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. For GBPUSD Bid, price is decreased by 2 points, and Ask is increased by 2 points.

<a id="prices-round-off"></a>
## Prices Round Off (#prices-round-off)

During the gateway's operation, accuracy of quotes (decimal places) passed for some symbol may change in the external trading system. Decrease in price accuracy at the external trading system's side does not affect the gateway's operation. It still transmits prices with less accuracy. However, if the number of decimal places at the external system's side increases, the gateway starts rounding off the passed prices.

Suppose that the accuracy of quotes has changed from 4 to 5 digits. Obtained five-digit quotes are rounded up by the gateway and used for creating the Market Depth. The round off is always performed in broker's favor. Thus, buy requests of 1.23447, 1.23441 are rounded up to 1.2345, while sell ones of 1.23447, 1.23441 are rounded down to 1.23440.

Changes in symbol price accuracy are recorded in the gateway journal.

```

---

<a id='gateways-currenex-md'></a>
### 119. `Gateways/Currenex.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / Currenex

[Previous](Integral.md) | [Next](Euronext-FX.md)

<a id="metatrader-5-gateway-to-currenex"></a>
# MetaTrader 5 Gateway to Currenex (#metatrader-5-gateway-to-currenex)

MetaTrader 5 Gateway to Currenex is a simple, fast and secure integration solution for brokers. The gateway provides liquidity when working in MetaTrader 5. [Currenex](https://www.currenex.com/) forex means the best quotations, sound liquidity and the most efficient orders execution with use of hi-tech solutions which were applied in the platform development and which allow to create the quickest electronic trading system.

<a id="about-the-company"></a>
## About the company (#about-the-company)

Founded in 1999, [Currenex](https://www.currenex.com/), offers corporate and institutional buyers and sellers in the FX and money markets reliable, low-cost and secure electronic access to the $1+ trillion a day global FX market.

Currenex platform represents one of the largest ECNsystems operating with forex instruments and getting feed from more than seventy largest financial organizations. Direct quotations provide users with the ability of complete independent, transparent and reliable control over the prices which precisely reflect the market situation in every point of time.

What Currenex offers:

  * 28 currency pairs available for trading
  * instant orders execution
  * an access to level2 and to real market volumes
  * narrow spreads
  * no re-quotation
  * Non Dealing Desk (NDD) technology
  * expanded list of orders (Standard, Conditional)
  * all transactions information is protected, absolute confidentiality



<a id="getting-started-with-currenex"></a>
## Getting started with Currenex (#getting-started-with-currenex)

In order to be able to provide trading services using Currenex, a brokerage company must first contact Currenex Sales Department for concluding the agreement: Contact details are given in the table below:

| Sales department | Friendly support  
New York | +1 212 340 1780 | +1 212 340 1780  
London | +44 (0) 20 3395 7930 | +44 (0) 20 3395 7930  
Tokyo | +81 3 4530 7555 | +81 3 4530 7555  
Singapore | +65 6826 7476 | +65 6826 7476  
Australia | +612 8429 1204 | +612 8429 1204  
| [sales@currenex.com](mailto:sales@currenex.com) | [support@currenex.com](mailto:support@currenex.com)  
| [www.currenex.com](https://www.currenex.com/) | [www.currenex.com](https://www.currenex.com/)  
  
After conclusion of an agreement, all necessary data for connection to the Currenex server will be provided to the brokerage company. Additional information is available on the official website [www.currenex.com](https://www.currenex.com/).

> [Order MetaTrader 5 Currenex Gateway](https://support.metaquotes.net/en/market/product/261)

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

MetaTrader 5 Gateway to Currenex is a separate CurrenexGateway64.exe module that uses the MetaTrader 5 Gateway API for operation. The gateway operates as a mediator between two systems connecting Currenex and MetaTrader 5 platform. All data between Currenex and the gateway is transmitted using FIX protocol over the encrypted connection. The gateway sends encrypted FIX messages and returns them to the MetaTrader 5 platform using MetaTrader 5 Gateway API.

<a id="market-data"></a>
### Market Data (#market-data)

MetaTrader 5 Gateway to Currenex automatically imports all the necessary symbols and processes their properties. An administrator only needs to perform primary setup as described bellow. Price data is transmitted in real time. The gateway allows to transmit the initial price data provided by Currenex or transform them. In the latter case quotes, reports and orders prices, that are directed to the client terminals, will be transformed according to the applied settings. Detailed information on prices conversion is available below.

<a id="trading-operations"></a>
### Trading Operations (#trading-operations)

Orders will be sent to MetaTrader 5 Currenex Gateway for processing in accordance with the configured routing rules. Processing of requests depends on the type of the order, as well as in the gateway configuration.

Order type | Execution  
---|---  
Market Order | Delivered directly to Currenex as a market order.  
Take Profit Buy Limit Sell Limit | Depends on LimitOrdersCoverage: LimitOrdersCoverage=Gateway (default) Limit orders are processed on the side of Currenex. Once a limit order has been placed by a client, an appropriate order is sent to Currenex. Take Profit orders are processed the same way as in the Limit mode. The Currenex system checks the availability of the required amount of funds to cover any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out. Margin reservation of the clients should be configured for the appropriate order types in case Limit orders are directly delivered to an external system. By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client. LimitOrdersCoverage=Limit Limit Orders and Take Profit orders are processed on the side of the MetaTrader 5. Once a limit order is triggered, an equivalent limit order is sent to Currenex. That order has a short action time specified in LimitOrdersCoverageTimeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Currenex. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5. A limit order with the price equal to a Take Profit level is sent to Currenex at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Currenex. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on MetaTrader 5 side.   
Limit mode allows to protect against slippage, as a limit order is sent to Currenex system with a specified price rather than a market order for execution by the current price. LimitOrdersCoverage=Market Limit orders and Take Profit orders are processed on the MetaTrader 5 platform side. Once they trigger, an appropriate market order us sent to Currenex.  
Buy Stop Sell Stop Stop Loss Stop Out | Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to Currenex system.  
Buy Stop Limit Sell Stop Limit | Processed on the MetaTrader 5 side. Upon order order activation, an appropriate limit order is created in MetaTrader 5, and this order is then processed in accordance with the value of the LimitOrdersCoverage parameter.  
  
  * In case connection to Currenex server is lost, the application will try to restore it repeatedly. In case pending orders have been executed at that, they will be updated in the MetaTrader 5 platform after connection is restored.
  * The Currenex system allows a broker to cancel orders in case of connection loss. The Currenex system does not cancel orders by default in that case but, nevertheless, you should notify the Currenex technical support about the necessity to disable that option for your account (pending orders should not be deleted in case of connection loss).
  * The gateway supports multiple modes of trade operation delivery to Currenex: on behalf of the broker's general account and on behalf of the individual accounts used for trading in MetaTrader 5 platform.

  
---  
  
<a id="gateway-setup"></a>
## Gateway Setup (#gateway-setup)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway Settings](images/currenex_common.png)

Set the following parameters on the "Common" tab:

  * ID â unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Module â specify CurrenexGateway64 and accept the default settings after the module selection.
  * Trading server â Currenex server IP-address and the port, where trade requests are processed. This information is provided by Currenex. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.
  * Trading login â a login for connection to the Currenex server. It is provided by Currenex as the 'trading comp id' parameter.
  * Password â a password for connection to the Currenex server. It is also provided by Currenex.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The data for connection to the Currenex server, where trade requests are processed, is submitted during the agreement conclusion.

  
---  
  
Other parameters are set similarly to other gateways. Default values are used in most cases.

Now, go to the "Parameters" tab.

![Gateway parameters setup](images/currenex_param.png)

Specify the following parameters values here:

  * FIX TargetCompID â a standard parameter of the FIX messages heading used for trading messages recipient identification. This parameter is provided by Currenex and is usually equal to CNX.
  * FIX Market Data ClientCompID â a standard parameter of the FIX messages heading used for a data sender identification. It is provided by Currenex as the 'market data comp id' parameter.


  * FIX Market Data Log Enabled â if "YES" is set, the gateway will save to disk the full quoting connection log. This can be useful in operation debugging. The log is not saved by default (value "No").
  * FIX Market Data Password â password for connecting to the market data stream. If the parameter is not specified or has an empty value, the trading connection password is used. The parameter is empty by default.


  * Account Mapping Mode â the gateway supports multiple modes of trade operation delivery to Currenex: on behalf of the broker's general account and on behalf of the individual accounts used for trading in MetaTrader 5 platform. Three modes of trades operations transfer are available:
    * omnibus â all orders will be transferred to Currenex on behalf of the broker's main account, specified in the "Trading login" parameter;
    * one-to-one â all orders will be transferred to Currenex on behalf of the individual accounts, at which they are set in MetaTrader 5 (account in the external system is displayed in each account's settings);
    * conversion â combination of the previous two modes: orders of the accounts that have specified external system account will be transferred on their own behalf, while all other orders will be transferred on behalf of the broker's general account.
  * Limit Orders Coverage Mode â the mode of processing of Limit and Take Profit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:
    * Market â limit and Take Profit orders are processed on the MetaTrader 5 platform side. Once the order triggers, an appropriate market order is sent to Currenex.
    * Limit â limit and Take Profit orders are processed on the MetaTrader 5 side.  
  
Once a limit order is triggered, an equivalent limit order is sent to Currenex. That order has a short action time specified in Limit Orders Coverage ModeTimeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Currenex. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.  
  
A limit order with the price equal to a Take Profit level is sent to Currenex at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Currenex. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on the MetaTrader 5 side.  
  
The Limit mode allows to protect against slippage, as a limit order is sent to the Currenex system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to Currenex.
    * Gateway â limit orders are processed on the Currenex side. Once a limit order has been placed by a client, an appropriate order is sent to Currenex. Take Profit orders are processed the same way as in the Limit mode.
  * Limit Orders Coverage Timeout â expiry of Limit Orders that are sent to Currenex in the Limit mode. Specified in seconds. The default value is 5. The minimal value is 2.
  * FIX Market Data Address â the IP address and port of the Currenex server, from which market data are transmitted. This information is provided by Currenex. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.


  * Weekend Trading Enabled â allow the gateway to process trading operations on weekends. The parameter can be set to Yes or No (default). If the parameter is absent or is set to No, trading on weekends is prohibited. For further details please see [Operation on Weekend](../../Platform-Setup/Gateways/Operation-on-Weekend.md).


  * Quotes Delay â delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample â the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample â the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample â the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



For connection to the system, Currenex requires authentication with a certificate. To obtain the certificate, use the [dedicated Currenex service](https://dret-dl.currenex.com/selfservice/selfservice.html), and then configure the corresponding settings in your gateway:

  * FIX Trade Certificate Path â the path to the client certificate store for FIX trading connections. If this parameter is missing or empty, the client certificate for trading connections will not be used. Therefore, this update will not affect brokers already using the gateway.  
  
If set to Local Machine (the default), the gateway will use the certificate from the Local Machine personal store of the operating system where it is installed. For proper operation, the certificate must be imported into this store.  
  
If a path is specified, the certificate will be loaded from a file in PFX (P12) format.  
  
After adding the parameter, the gateway will retrieve the certificate from the specified store (system or file). The search is conducted using the CN (Common Name) field, which must match the trading connection login (ClientCompID) specified in the Trade Login parameter.  

  * FIX Trade Certificate Password â password to open the PFX certificate file for the trade connection.
  * FIX Market Data Certificate Path â works similarly to FIX Trade Certificate Path but is used for the quote connection. The certificate search in the specified store is performed by the CN (Common Name) field, which must match the quoting connection login (ClientCompID) specified in the 'FIX Market Data ClientCompID' parameter.
  * FIX Market Data Certificate Password â password to open the PFX certificate file for the quoting connection.



  * In no circumstances it is allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.
  * When Limit orders are directly delivered to an external system, margin reservation of the clients should be configured for the appropriate order type.

  
---  
  
The next stage is to specify the groups of the clients, whose requests will be processed via the gateway. All groups are configured on the screenshot below, but you can configure groups according to your business logic.

![Configuration of groups](images/currenex_groups.png)

Then configure the list of symbols, according to which the gateway will process trade operations and feed quotes.

![Configuring the symbols](images/currenex_symbols.png)

Make sure to enable "Allow importing symbol settings" option. The symbols available to Currenex will be imported to Symbols/Preliminary/Currenex directory of the MetaTrader 5 platform. Besides, that will allow the gateway to manage the settings of the symbols used in trading via Currenex.

  * The symbols imported by the gateway are put to the "\Preliminary" symbols subgroup. All symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After symbols are relocated and trading abilities are enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case the symbol is not transferred and its trading ability is not turned off.
  * In case some changes are implemented to the Depth of Market parameter of the symbol settings, Currenex gateway and a history server must be restarted to let the changes take effect. In fact, restart is required after any change in the symbol settings.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="margin"></a>
## Margin Setup (#margin)

When Limit orders are directly delivered to an external system, margin reservation of the clients should be configured for the appropriate order type.

The external system checks sufficiency of the funds that are necessary to provide any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out.

By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client.

After an order has been transferred to the external system, MetaTrader 5 platform is not able to check the client's margin sufficiency any more. After the order has been executed in the external system, the gateway cannot ignore that fact. Therefore, the appropriate trading operation is performed in the platform.

Set non-zero coefficients for the orders directly transferred to the external trading system in symbol settings for the appropriate symbols to configure margin collection:

![Margin Setup](images/currenex_margin.png)

<a id="routing"></a>
## Configuring trade requests routing (#routing)

Configure the routing to let the clients requests to be transmitted to the Currenex gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

In the figure below all client orders created by users in the demo\demoforex group having symbols from Forex\Currenex group will be sent to the gateway for processing.

![Configuring routing](images/currenex_routing.png)

After the correct execution of the steps described above, the gateway will be ready for work.

<a id="markup"></a>
## Changing symbols names and prices correction (#markup)

The gateway the price flow from the Currenex system to the MetaTrader 5 platform and controls settings of appropriate symbols. In addition, the gateway allows you to edit quotes and Market Depth data transmitted to clients from an external system.

The gateway receives prices from Currenex and delivers them to clients taking into account conversion settings. Clients perform trading operations using converted prices. However, while processing trading operations on the gateway and their transmission to Currenex , initial, not converted prices are automatically used.

Thus, by increasing the selling price and reducing the purchase price ("price spreading") a brokerage company receives its profit share from each deal performed at Currenex . The correction value is set separately for each symbol on the "Translations" tab:

![Configuring transformations](images/currenex_translation.png)

Here you can configure matching of symbol names used in Currenex with the names used in your MetaTrader 5 platform. For example, if the symbol name in Currenex is EURGBPCNX, and it is called EURGBP in the MetaTrader 5, enter EURGBP in the "Symbol" field and EURGBPCNX in the "Source" field.

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. Below is a schematic example of the conversion:

Currenex | >>> | ask price | EURGBP 0.83004 | >>> | MetaTrader 5 server  
---|---|---|---|---|---  
MetaTrader 5 server | >>> | ask price | EURGBP 0.83006 | >>> | Client terminal  
Client terminal | >>> | buy limit | EURGBP 0.83006 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit | EURGBP 0.83004 | >>> | Currenex  
Currenex | >>> | buy limit execution | EURGBP 0.83004 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit execution | EURGBP 0.83006 | >>> | Client terminal  
  
A broker gains 2 pips of profit in this example. The price is sent to the client terminal only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices submitted by Currenex.

<a id="prices-round-off"></a>
## Prices Round Off (#prices-round-off)

During the gateway's operation, accuracy of quotes (decimal places) passed for some symbol may change in the external trading system. Decrease in price accuracy at the external trading system's side does not affect the gateway's operation. It still transmits prices with less accuracy. However, if the number of decimal places at the external system's side increases, the gateway starts rounding off the passed prices.

Suppose that the accuracy of quotes has changed from 4 to 5 digits. Obtained five-digit quotes are rounded up by the gateway and used for creating the Market Depth. The round off is always performed in broker's favor. Thus, buy requests of 1.23447, 1.23441 are rounded up to 1.2345, while sell ones of 1.23447, 1.23441 are rounded down to 1.23440.

Changes in symbol price accuracy are recorded in the gateway journal.

<a id="multiaccount"></a>
## Trade Operations Transfer Modes (#multiaccount)

The MetaTrader 5 Gateway to Currenex allows to send trade operations to Currenex using different modes. Trading orders placed by clients in the MetaTrader 5 platform can be sent to on behalf of the broker's general account (specified in the "Trading login" parameter of the gateway settings) or on behalf of the clients' individual accounts. In the latter case, gateway connection to Currenex is performed via broker's general account. However, clients' trade operations are executed on Currenex on individual accounts.

  * Order sending mode is controlled by the Account Mapping Mode parameter in the gateway configuration.
  * Trade operations transfer conditions are determined while concluding an agreement between a brokerage company and Currenex.
  * In no circumstances it is allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.



If you send trading operations using individual client accounts, the appropriate Currenex account number must be specified in each account's settings. This can be done in the [Administrator (#trade-accounts)](../../Platform-Setup/Accounts/Editing-Account.md#trade-accounts) or [Manager](https://support.metaquotes.net/en/docs/mt5/manager/management/management_accounts/account_view/account_view_account) terminal:

![Client's account in the external trading system](images/currenex_account.png)

In "Trade accounts" section, select Currenex gateway configuration and specify the client's account in the external system. That is the account, from which client trade operations will be transferred to Currenex.

Clients' account numbers are submitted by Currenex.

```

---

<a id='gateways-dgcx-md'></a>
### 119. `Gateways/DGCX.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / DGCX

[Previous](MOEX-Derivatives.md) | [Next](MetaTrader-5.md)

<a id="metatrader-5-gateway-to-dgcx"></a>
# MetaTrader 5 Gateway to DGCX (#metatrader-5-gateway-to-dgcx)

MetaTrader 5 Gateway to DGCX allows trading on [the Dubai Gold and Commodities Exchange](https://www.dgcx.ae/).

<a id="about-dubai-gold-and-commodities-exchange"></a>
## About Dubai Gold and Commodities Exchange (#about-dubai-gold-and-commodities-exchange)

Dubai has historically been an international hub for the physical trade of not only gold, but also many other commodities. So the establishment of the [Dubai Gold & Commodities Exchange (DGCX)](https://www.dgcx.ae/dgcx/about-dgcx) was the next logical step for the region and the local economy. DGCX commenced trading in November 2005 as the region's first commodity derivatives exchange. Today it is the leading derivatives exchange in the Middle East.

<a id="benefits-of-trading-on-dgcx"></a>
## Benefits of Trading on DGCX (#benefits-of-trading-on-dgcx)

DGCX range of futures contracts offers participants of the physical commodities markets, such as producers, manufacturers and end users, a sophisticated means of hedging their price risk exposure. Such price risk management has previously been unavailable to producers in the Middle East. In addition, DGCX offers trading opportunities to financial communities and investment houses in both the Middle East and around the globe that wish to access the growing asset class of commodity and currency derivatives.

  * Guaranteed settlement and reduced counterparty risk provided by Dubai Commodities Clearing Corporation (DCCC), a subsidiary 100% owned by DGCX
  * The advantage of transacting and clearing business within the UAE and thus the local taxation and regulatory regimes
  * A simple fee structure - one fee for all participants. All participants also pay the same margin, whether commercial or non-commercial entities
  * Access to both regional and international liquidity pools
  * Robust risk management and surveillance systems
  * Uninterrupted trading hours from 7:00 to 23:30 (GMT +04:00)
  * Regulated by the Emirates Securities & Commodities Authority (ESCA)



<a id="product-portfolio"></a>
## Product Portfolio (#product-portfolio)

The UAE enjoys an ideal location between the time zones of Europe and the Far East and DGCX offers a range of products from the precious metal, base metal, energy and currency sectors.

Futures | Options  
---|---  
Precious metals | Currencies | Energy resources | Base metals |   
Gold Silver | Australian Dollar/US Dollar British Sterling/US Dollar Canadian Dollar/US Dollar Euro/US Dollar Indian Rupee/US Dollar Japanese Yen/US Dollar Swiss Franc/US Dollar | WTI Light Sweet Crude Oil Brent Crude Oil Fuajairah 380 CSR Fuel Oil | Steel Rebar | Options on Gold Futures Options on INR Futures  
  
<a id="how-to-become-a-broker-at-dgcx"></a>
## How to become a broker at DGCX (#how-to-become-a-broker-at-dgcx)

All rules of the Dubai exchange can be found in [Regulatory section of the official web site](https://www.dgcx.ae/regulatory/overview). The information on how to become a member and start providing brokerage services on the exchange can also be found at [Membership](https://www.dgcx.ae/membership/overview) section of the official web site. Additionally, you can contact DGCX via e-mail [support@dgcx.ae](mailto:support@dgcx.ae). After obtaining the necessary information and registering as a market member, it is time to configure the gateway.

> [Order MetaTrader 5 DGCX Gateway](https://support.metaquotes.net/en/market/product/276)

<a id="preparing-for-the-gateway-launch-configuring-vpn"></a>
## Preparing for the Gateway Launch, Configuring VPN (#preparing-for-the-gateway-launch-configuring-vpn)

Before setting a brokerage company gateway, configure the virtual network channel to be able to connect to DGCX servers.

Configuration of a virtual network channel is performed together with DGCX technical specialists. To create a virtual channel to DGCX, a broker must request technical requirements and recommendations for connection to the DGCX virtual private network (VPN) from the exchange technical support team. After obtaining the necessary information a brokerage company should purchase a recommended router.

At the next stage the mercantile exchange technical support team will submit to the brokerage company description of the equipment settings on DGCX side: tunnel type, data encryption method, data encryption keys etc. The router must be configured according to the obtained data.

In addition, the brokerage company must specify its own equipment parameters and send this information to the mercantile exchange technical support team in the form received from DGCX. When all agreed equipment settings are configured at both a brokerage company and the exchange sides, the virtual channel for connection to DGCX will be ready for operation.

You can skip procedures related to establishing connection and to setting up secure access channels, by safely locating the gateway on a ready-made server provided by the exchange (collocation). It can be used in [remote mode](../../Platform-Setup/Gateways/Setup-as-Service.md) through a regular connection. For further collocation details please [contact Service Desk](https://support.metaquotes.net/en/support).

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

Gateway operates mainly as a mediator between two systems connecting DGCX and MetaTrader 5 platform. The gateway establishes several connections to DGCX server for the data exchange via the created virtual channel:

  * The first connection is used for performing trading operations and working according to FIX (Financial Information eXchange) protocol.
  * The second one is used to obtain quotation data and utilizes a broadcast data transfer binary protocol (EMAPI). Data can be transferred both via TCP and UDP multicast protocol.
  * In addition, the gateway can establish the third connection to DGCX FTP server to get special risk parameters files used for calculating margin requirements and files containing data on opened client positions.



![Gateway operation scheme](images/dgcx_scheme.png)

The broker's servers are configured in such a way that the clients' trade requests are sent to MetaTrader 5 DGCX Gateway. The gateway checks correctness of the client requests. In case validation is successful, the relevant trade request is directed to DGCX server via a standard protocol for exchanging financial information - FIX. After receiving a response from the DGCX server, the gateway saves the trade request processing result in the platform, which in its turn reports this result to the trader.

Orders are sent to MetaTrader 5 DGCX Gateway for processing in accordance with the set routing rules. Depending on the order type, each request is handled differently:

  * Market orders are transferred to DGCX system directly. In case there is no liquidity for a requested financial instrument, the market order is rejected.
  * Limit orders are processed at DGCX. Once a limit order has been placed, it is sent to DGCX server. There it is placed to the general requests queue awaiting for an opposite request with the same price to appear. Thus, clients can see their requests in the Depth of Market in the client terminal in real time.
  * Stop orders are sent to DGCX immediately after being placed. When the specified stop price is reached, stop order is activated on a stock exchange and an appropriate market order is sent to MetaTrader 5 platform.
  * Stop-limit orders are handled and stored on DGCX server until their stop price is reached. Once a stop-limit order has been triggered, the corresponding limit order with a specified price will be sent to MetaTrader 5 platform.
  * Take Profit and Stop Loss levels for the current open positions are controlled by MetaTrader 5 platform. In case of Stop Loss activation, a market order to close a client's position is sent to the exchange. In case of Take Profit activation, a limit order at the Take Profit price is sent to the exchange.
  * Stop out of positions and orders is controlled by the trading platform. In case a limit order must be removed after a Stop out level has been reached, an appropriate request for its removal is sent to DGCX server. In case a position must be closed because of Stop out, a market request to close a client's position is sent to the exchange.



<a id="metatrader-5-dgcx-gateway-setup"></a>
## MetaTrader 5 DGCX Gateway Setup (#metatrader-5-dgcx-gateway-setup)

MetaTrader 5 DGCX Gateway is a separate "DGCXGateway64.exe" file that uses Gateway API for its operation. The gateway module is included in the platform delivery set and available for use in test mode. In this mode the number of trade operations is limited - after the limit is reached they will not be processed. To switch to the full version, [order the MetaTrader 5 Gateway to DGCX Gateway](https://support.metaquotes.net/en/market).

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Configuring MetaTrader 5 Gateway to DGCX](images/dgcx_common.png)

The following parameters on the "Common" tab must be set:

  * Module — DGCXGateway64. After that the gateway default parameters installation must be allowed in the dialog request.
  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Trading server — DGCX FIX server address must be entered in this field in the "address:port" format. The demo server address "10.30.30.126:7250" is shown in the provided example.
  * Trading login — user ID for FIX connection to DGCX (User id). The value 20041 is shown in the provided example.
  * Trading password — user password for FIX connection to DGCX.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The data for connection to the DGCX server, where trade requests are processed, is submitted during the agreement conclusion.

  
---  
  
Additional configuration parameters should be set on the Parameters tab:

![Configuring MetaTrader 5 Gateway to DGCX](images/dgcx_param.png)

Additional options should be provided by DGCX in the brokerage company connection specification. 

  * Use Multicast Data — parameter defining the necessity of receiving quotes via UDP multicast connection. To do this, the value of the parameter should be set to "Yes" or "Y". Otherwise, TCP connection will be used to receive the quotes.
  * Bind Address — address of the network interface the gateway will interact with. The address is used in case there are several network interfaces on the computer, at which the gateway is operating.
  * FIX Second Address — address of the backup DGCX FIX server in "address:port" format. This server is automatically used in case it has been impossible to connect to the main FIX server after several attempts. The demo server address "10.30.30.127:7250" is shown in the provided example.
  * FIX TargetCompID — FIX messages heading standard parameter. This parameter is used to identify a recipient of trading messages. The parameter value is provided by DGCX.
  * FIX Broker Account — broker's trading account ID. It is used when all clients trade using a single general account.
  * FIX News Recipients — list of logins of MetaTrader clients separated by ";". These clients will receive e-mails containing news sent by DGCX.
  * EMAPI Address — main address for connecting to the DGCX "prelogon" channel in the "address:port" format. In the provided example, this is the address of the demo server "10.30.30.126:6970". The "prelogon" channel is used for a preliminary connection to the exchange. The gateway receives the exchange main working address from it (the "logon" channel). After that, the gateway connects to it for further operation.
  * EMAPI Second Address — backup address for connecting to the DGCX "prelogon" channel in the "address:port" format. The system automatically switches to the server in case the main EMAPI server remains unavailable after several connection attempts. In the provided example, this is the address of the demo server "10.30.30.128:6970".
  * EMAPI Logon Address — "logon" address of the DGCX channel in the "address:port" format. This parameter allows redefining the address of the exchange main working server. If the parameter is set, connection is performed to the specified address rather than to the address obtained via the "prelogon" channel.
  * EMAPI MemberID — EMAPI member ID. The parameter value is provided by DGCX.
  * EMAPI UserID — EMAPI user ID. The parameter value is provided by DGCX.
  * EMAPI Password — EMAPI user password. The parameter value is provided by DGCX.
  * FTP Span Url — full path to the folder on the exchange's FTP server where the risk parameters files (SPAN risk parameter file) are stored. These files are used to calculate margin requirements. This connection is also used for receiving files containing data on opened client positions. The ftp or sftp protocols are supported. If the protocol is not specified explicitly in the address, ftp is used. The default value is sftp://eosftp.dgcx.ae:6022/Common/Parameter.
  * FTP Login — login for connection to the FTP server. The parameter is provided by DGCX.
  * FTP Password — password for connection to the FTP server. The parameter is provided by DGCX.
  * Import Span Spreads — if you set this parameter to "Yes", the gateway will import [spreads](../../Platform-Setup/Spreads.md). The default value is "No".
  * FTP Market Stats Url — an address of the folder on an FTP server, from which the gateway takes the market statistics files. The login and password used to receive span files are used for connection (the FTP Login and FTP Password parameters). The ftp or sftp protocols are supported. If the protocol is not specified explicitly in the address, ftp is used. The default value is sftp://eosftp.dgcx.ae:6022/Common/MarketStatistics.
  * TP Orders Coverage Timeout — Take Profit order expiration time in seconds. Take Profit orders execution is tracked on the MetaTrader 5 platform side. When triggered, an appropriate limit order for closing a position at the price of an activated Take Profit is sent to the market. The order lifetime is 20 seconds by default. If the exchange does not execute the order within this time, the order will be canceled. In this case, the Take Profit activation attribute is removed on the platform side. If the Take Profit is activated again on the next tick, another limit order is sent to the exchange.  
This behavior is implemented so that an order does not wait for its execution at an exchange for an indefinite period of time.   
The TP Orders Coverage Timeout parameter allows re-defining the lifetime of limit orders sent to an exchange when Take Profit is triggered. Set the necessary value in seconds. If there is no parameter, the value of 20 seconds is used.
  * Symbols Path — path to which trading symbols from the exchange will be imported. The parameter is absent by default and the gateway imports trading instruments to the \Preliminary\DGCX subgroup, with the disabled trading option. The system administrator should manually move the symbols to the proper group and enable trading for them. If the parameter is present, the gateway will import trading instruments to the specified path. In this case, the trading option will be immediately enabled. Thus, there is no need for the administrator need to configure the symbols. For example, if "DGCX-Real" is specified in the parameter, the symbols will be automatically added to the DGCX-Real\* group, while expired contracts will be moved to DGCX-Real\Expired\*.
  * Symbols Path Expired — path to move expired symbols. The parameter is not specified by default, and the gateway moves all expired contracts to the \Expired subdirectory of the directory specified in "Symbols Path". In the above example, it is DGCX-Real\Expired\*. By creating this parameter, you can override the path.
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



The groups of the clients, whose requests will be processed via MetaTrader 5 DGCX Gateway, should be specified at the "Groups" tab.

![Configuring groups for MetaTrader 5 Gateway to MOEX Derivatives](images/dgcx_groups.png)

The "Symbols" tab allows configuring the list of symbols, according to which the gateway will process trade operations and transmit the quotes.

![Configuring symbols for MetaTrader 5 Gateway to MOEX Derivatives](images/dgcx_symbols.png)

Make sure to enable "Allow importing symbol settings" option. The gateway imports symbols from the DGCX to the MetaTrader 5 platform in accordance with the Symbols Path parameter. Then, in the future, the gateway will control the parameters of these symbols. In addition to various trading settings, trading and quotation sessions are also imported by symbols considering the time zones MetaTrader 5 platform and DGCX work in (GMT +04:00).

> The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

<a id="routing"></a>
## Configuring Trade Requests Routing (#routing)

The next step is configuring the routing to let the clients requests to be transmitted to the DGCX gateway. To do this, add a [routing rule](../../Platform-Setup/Routing.md).

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions you may indicate the groups of clients, whose requests will be passed to the gateway, and the symbols, trading operations with which will be also passed to the gateway.

In the figure below all client orders by symbols from the DGCX\* group will be sent to the gateway for processing.

![Configuring routing rules](images/dgcx_routing_common.png)

Only DGCX gateway should be added at the "Dealers" tab:

![Configuring routing rules](images/dgcx_routing_dealer.png)

<a id="swap-setup"></a>
## Swap Setup (#swap-setup)

Swap size can be adjusted for specific symbols via the gateway parameters in the format <Symbol_name>-Swap = <Swap value>. The screenshot shows configuration of the DGSG symbol as an example:

![Swap Setup](images/dgcx_swap.png)

<a id="passwords"></a>
## Gateway Launch (#passwords)

After the application of all settings described above, your gateway is almost ready to go. It will connect to DGCX server.

2013.04.01 11:06:22 Gateway 'DGCX Gateway' starting  
2013.04.01 11:06:23 Gateway license check succeeded  
2013.04.01 11:06:23 Gateway emapi: establishing prelogon connection to DGCX EMAPI server (10.30.30.126:6970)  
2013.04.01 11:06:24 Gateway emapi: prelogon completed  
2013.04.01 11:06:24 Gateway emapi: establishing logon connection to DGCX EMAPI server (10.30.30.128:6970)  
2013.04.01 11:06:24 Gateway emapi: logon completed  
2013.04.01 11:06:26 Gateway emapi: reference data synchronized  
2013.04.01 11:06:28 Gateway emapi: subscription groups data synchronized  
2013.04.01 11:06:28 Gateway connecting to DGCX FIX server (10.30.30.126:7250)  
2013.04.01 11:06:29 Gateway fix: logged on  
2013.04.01 11:06:29 Gateway synchronized with DGCX exchange  
---  
  
The last entry means that the gateway has successfully connected to DGCX and is now ready for operation. In case of connection failure, the entries concerning the failure reasons appear in the gateway journal.

New symbols are imported after the first connection. As noted above, the newly added symbols must be relocated from "Preliminary" group and trading for them must be allowed. After that the MetaTrader 5 platform main trade server must be restarted. These actions should be performed only during the gateway first launch.

After the main trading server is restarted, the gateway installation and configuration is complete. Traders can perform transactions on DGCX using their MetaTrader 5 client terminal.

<a id="gateway-operation"></a>
## Gateway Operation (#gateway-operation)

This section describes the standard procedures performed by the gateway during its operation.

<a id="updating-the-symbols-settings"></a>
### Updating the Symbols Settings (#updating-the-symbols-settings)

The gateway automatically updates the symbols settings during its operation, if necessary. Appropriate entries appear in the journal in that case:

2013.04.01 11:06:30 SymbolsBase symbol 'DS-20130906' config updated  
---  
  
<a id="multi-leg-instruments"></a>
### Multi-leg Instruments (#multi-leg-instruments)

DGCX provides possibility to trade multi-leg instruments. These are the instruments consisting of several subinstruments allowing to implement definite hedging strategies in trading. Such symbols are not supported by MetaTrader 5 platform and it is impossible to import them.

<a id="risk"></a>
### Risk Parameters (#risk)

During a trading day and at the end of it DGCX publishes special span files on its FTP servers. These span files contain risk management parameters. The gateway downloads the files to \Gateway\DGCXGateway\DGCX Gateway\ftp\ directory on the history server and uses the obtained data for recalculation of margin requirements and accrual of the variation margin at the end of the trading session.

  * The files having dgcxrpf-20130320-0600-01-i.spn format contain intraday risk management parameters.
  * The files having dgcxrpf-20130321-2345-01-e.spn contain risk management parameters for the end of a trading session.



The following entries are shown in the gateway journal when downloading and processing risk parameters files:

10:51:22 Gateway span: downloaded file dgcxrpf-20130326-1500-02-i.spn (267 Kb)  
10:51:22 Gateway span: data processing completed, 95 span data records found  
---

```

---

<a id='gateways-euronext-fx-md'></a>
### 119. `Gateways/Euronext-FX.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / Euronext FX

[Previous](Currenex.md) | [Next](Cboe-FX.md)

<a id="metatrader-5-euronext-fx-gateway"></a>
# MetaTrader 5 Euronext FX Gateway (#metatrader-5-euronext-fx-gateway)

Euronext FX is a heavy-duty matching system of foreign exchange, Euronext FX offers its customers access to a large pool of diversified liquidity at unparalleled speed, complete transparency, and excellent customer service. MetaTrader 5 Euronext FX Gateway is a simple, fast and secure integration solution for brokers.

Integration provides:

  * Liquidity. Euronext FX provides services to various clients including brokerage companies, banks, hedge funds and other organizations. Together they form a unique pool of liquidity.
  * Speed. Euronext FX offers a trading environment with ultra-low latency. The Euronext FX system's average delay of the full data sending and receiving cycle equals to 200 microseconds with a standard deviation of 50 microseconds. The delay in the full cycle is measured as the time required to deliver a client's message to Euronext FX, to process it and to send it back to the client.
  * Transparency. Customers can see quotes and trades with corresponding prices and volumes without delays in real time. The execution price is selected in accordance with a strict priority order: Price/Volume/Placing time. As soon as a better price appears, it is immediately sent to the liquidity recipient.



<a id="actions"></a>
## Getting started with Euronext FX (#actions)

In order to be able to provide trading services using Euronext FX, you should first contact the sales department for concluding the agreement:

Sales department | Friendly support  
---|---  
+442079033826 | +16464322940  
[sales@fastmatchfx.com](mailto:sales@fastmatchfx.com) | [support@fastmatchfx.com](mailto:support@fastmatchfx.com)  
[www.euronextfx.com](https://www.euronextfx.com/) |   
  
Once you have an agreement with Euronext FX, you will be provided with further instructions on how to connect to the Euronext FX server. For more details please visit the official Euronext FX site at [www.euronextfx.com](https://www.euronextfx.com/).

> [Order the MetaTrader 5 Euronext FX Gateway](https://support.metaquotes.net/en/market/product/265)

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

MetaTrader 5 Euronext FX Gateway is a separate module that uses the MetaTrader 5 Gateway API for operation. The gateway operates as a mediator between two systems: Euronext FX and MetaTrader 5 platform. Data is transmitted using FIX protocol over the encrypted connection. The gateway translates FIX messages and communicates them back to MetaTrader 5 platform using MetaTrader 5 Gateway API.

There are two main types of data that flow through the gateway:

  * market data (quotes, reports);
  * trading messages.



![FastMatch Gateway operation scheme](images/fastmatch_scheme.png)

<a id="market-data"></a>
### Market Data (#market-data)

MetaTrader 5 Euronext FX Gateway automatically imports all the necessary symbols and processes their properties. An administrator only needs to perform primary [setup (#symbols)](Euronext-FX.md#symbols) described below. Price data is transmitted in real time. The gateway allows to transmit original price data provided by Euronext FX, as well as to convert them. In the latter case quotes, reports and orders prices, that are directed to the client terminals, will be transformed according to the applied settings. Detailed information on [prices conversion (#markup)](Euronext-FX.md#markup) is available below.

<a id="trading-operations"></a>
### Trading Operations (#trading-operations)

Orders will be sent to MetaTrader 5 Euronext FX Gateway for processing in accordance with the configured [routing rules (#routing)](Euronext-FX.md#routing). Processing of requests depends on the type of the order, as well as in the gateway configuration.

Order type | Execution  
---|---  
Market Order | Delivered directly to Currenex as a market order.  
Take Profit Buy Limit Sell Limit | Depends on [Limit Orders Coverage Mode (#parameters)](Euronext-FX.md#parameters): Limit Orders Coverage Mode=Gateway (default) Limit orders are processed on the side of Euronext FX. Once a limit order has been placed by a client, an appropriate order is sent to Euronext FX. There it is placed in the aggregate Depth of Market awaiting for an opposite request with the same price to appear. Thus, clients can see their requests in the Depth of Market in the client terminal in real time. Take Profit orders are processed the same way as in the Limit mode. The Euronext FX system checks the availability of the required amount of funds to cover any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out. [Margin reservation (#margin)](Euronext-FX.md#margin) of the clients should be configured for the appropriate order types in case Limit orders are directly delivered to an external system. By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client. Limit Orders Coverage Mode=Limit Limit Orders and Take Profit orders are processed on the side of the MetaTrader 5. Once a limit order is triggered, an equivalent limit order is sent to Euronext FX. That order has a short validity time specified in Limit Orders Coverage Timeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Euronext FX. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5. A limit order with the price equal to a Take Profit level is sent to Integral at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Euronext FX. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on MetaTrader 5 side.   
The Limit mode allows to protect against slippage, as a limit order is sent to the Euronext FX system with a specified price rather than a market order for execution by the current price. Limit Orders Coverage Mode=Market Limit orders and Take Profit orders are processed on the MetaTrader 5 platform side. Once they trigger, an appropriate market order us sent to Euronext FX.  
Buy Stop Sell Stop Stop Loss Stop Out | Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to the Euronext FX system.  
Buy Stop Limit Sell Stop Limit | Processed on the MetaTrader 5 side. Upon order order activation, an appropriate limit order is created in MetaTrader 5, and this order is then processed in accordance with the value of the Limit Orders Coverage Mode parameter.  
  
<a id="setup"></a>
## Gateway Setup (#setup)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway Settings](images/fastmatch_common.png)

Set the following parameters on the "Common" tab:

  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Module — specify EuronextFXGateway64 and accept the default settings after the module selection.
  * Trading server — Euronext FX server IP-address and the port, where trade requests are processed. This information is provided by Euronext FX. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.
  * Trading login — a login for connection to the Euronext FX server. It is provided by Euronext FX as the "trading comp id" parameter.
  * Password — password for connection to the Euronext FX server. It is also provided by Euronext FX.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The details for connection to the Euronext FX server, where trade requests are processed, will be provided with the agreement.

  
---  
  
Other parameters are set similarly to other gateways. Default values are used in most cases.

Now, go to the "Parameters" tab.

![Gateway settings](images/fastmatch_param.png)

Specify the following parameters values here:

  * FIX TargetCompID — a standard parameter of the FIX messages heading used for trading messages recipient identification. Provided by Euronext FX.
  * FIX Market Data SenderCompID — a standard parameter of the FIX messages heading used for a data sender identification. Provided by Euronext FX.
  * Account Mapping Mode — the gateway supports multiple [modes of trade operation delivery (#multiaccount)](Euronext-FX.md#multiaccount) to Euronext FX: on behalf of the broker's general account and on behalf of the individual accounts used for trading in MetaTrader 5 platform. Three modes of trades operations transfer are available:
    * omnibus — all orders will be transferred to Euronext FX on behalf of the broker's main account, specified in the "Trading login" parameter.
    * one-to-one — all orders will be transferred to Euronext FX on behalf of the individual accounts, at which they are set in MetaTrader 5 (account in the external system is displayed in each account's settings).
    * conversion — combination of the previous two modes: orders of the accounts that have specified external system account will be transferred on their own behalf, while all other orders will be transferred on behalf of the broker's general account.
  * Limit Orders Coverage Mode — the mode of processing of Limit and Take Profit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:
    * Market — limit and Take Profit orders are processed on the MetaTrader 5 platform side. Once a limit order triggers, an appropriate market order is sent to Euronext FX.
    * Limit — limit and Take Profit orders are processed on the MetaTrader 5 side.  
  
Once a limit order is activated, an appropriate limit order is sent to Euronext FX. The order has a short lifetime specified in the Limit Orders Coverage Timeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed.  
  
If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Euronext FX. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.  
  
A limit order with the price equal to a Take Profit level is sent to Euronext FX at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Euronext FX. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on the MetaTrader 5 side.  
  
Limit mode allows to protect against slippage, as a limit order is sent to the Euronext FX system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to Euronext FX.
    * Gateway — limit orders are processed on the Euronext FX side. Once a limit order has been placed by a client, an appropriate order is sent to Euronext FX. Take Profit orders are processed the same way as in the Limit mode.
  * Limit Orders Coverage Timeout — expiry of Limit Orders that are sent to Euronext FX in the Limit mode. Specified in seconds. The default value is 5.
  * FIX Market Data Address — the address of the server with market data in the format of ip:port. Provided by Euronext FX. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example, 10.123.100.18:10219/nossl.
  * FIX Market Data Log Enabled — if "YES" is set, the gateway will save to disk the full quoting connection log. This can be useful in operation debugging. The log is not saved by default (value "No").
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



  * It is not allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.
  * When Limit orders are directly delivered to an external system, [margin reservation (#margin)](Euronext-FX.md#margin) of the clients should be configured for the appropriate order type.


  * For correct operation, the gateway needs to receive messages regarding the trading session states. Request from the data provider 'Trading Session Status (35=h)' events which should be sent in your quoting connection.

  
---  
  
The next stage is to specify the groups of the clients, whose requests will be processed via the MetaTrader 5 Euronext FX Gateway. All groups are configured on the screenshot below, but you can configure groups according to your business logic.

![Configuration of groups](images/fastmatch_groups.png)

Then configure the list of symbols, according to which the gateway will process trade operations and feed quotes.

![Configuring the symbols](images/fastmatch_symbols.png)

Make sure to enable "Allow importing symbol settings" option. Symbols available to Euronext FX will be imported to the folder 'Symbols\Preliminary\EuronextFX' of the MetaTrader 5 platform. Besides, that will allow the gateway to manage the settings of the symbols used in trading via Euronext FXl.

  * The symbols imported by the gateway are put to the "\Preliminary" symbols subgroup. All symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After symbols are relocated and trading abilities are enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case the symbol is not transferred and its trading ability is not turned off.
  * In case some changes are implemented to the Depth of Market parameter of the symbol settings, the Euronext FX gateway and a history server must be restarted to let the changes take effect. Restart is required after any change in symbol settings.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="margin"></a>
## Margin Setup (#margin)

When Limit orders are directly delivered to an external system, margin reservation of the clients should be configured for the appropriate order type. The external system checks sufficiency of the funds that are necessary to provide any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out.

By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client.

After an order has been transferred to the external system, MetaTrader 5 platform is not able to check the client's margin sufficiency any more. After the order has been executed in the external system, the gateway cannot ignore that fact. Therefore, the appropriate trading operation is performed in the platform.

Set non-zero coefficients for the orders directly transferred to the external trading system in order to configure margin collection:

![Margin Setup](images/fastmatch_margin.png)

<a id="routing"></a>
## Configuring trade requests routing (#routing)

Configure the routing to let the clients requests to be transmitted to the Euronext FX gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway. In the picture below all orders for symbols from the "Euronext FX" group will be routed to the gateway for processing.

![Configuring trade requests routing](images/fastmatch_routing.png)asd

After the correct execution of the steps described above, Euronext FX Gateway will be ready for use.

<a id="markup"></a>
## Changing symbols names and prices correction (#markup)

The gateway the price flow from the Euronext FX system to the MetaTrader 5 platform and [controls settings of appropriate symbols (#symbols)](Currenex.md#symbols). The standard feature of gateways is the ability to change the quotes and market depth transmitted to the clients from an external system.

The gateway receives prices from Euronext FX and delivers them to clients taking into account conversion settings. Clients perform trading operations using converted prices. However, while processing trading operations on the gateway and their transmission to Euronext FX, initial, not converted prices are automatically used.

Thus, by increasing the selling price and reducing the purchase price ("price spreading") a brokerage company receives its profit share from each deal performed at Euronext FX. The correction value is set separately for each symbol on the "Translations" tab:

![Configuring Price Translation](images/fastmatch_translation.png)

Here you can configure matching of symbol names used in Euronext FX with the names used in your MetaTrader 5 platform. For example, if the symbol name in Euronext FX is EURUSDFM, and it is called EURUSD in the MetaTrader 5, enter EURUSD in the "Symbol" field and EURUSDFM in the "Source" field.

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. Below is a schematic example of the conversion:

Euronext FX | >>> | ask price | EURUSD 0.83004 | >>> | MetaTrader 5 server  
---|---|---|---|---|---  
MetaTrader 5 server | >>> | ask price | EURUSD 0.83006 | >>> | Client terminal  
Client terminal | >>> | buy limit | EURUSD 0.83006 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit | EURUSD 0.83004 | >>> | Euronext FX  
Euronext FX | >>> | buy limit execution | EURUSD 0.83004 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit execution | EURUSD 0.83006 | >>> | Client terminal  
  
A broker gains 2 pips of profit in the provided example. The price is sent to the client terminal only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices submitted by Euronext FX.

<a id="prices-round-off"></a>
## Prices Round Off (#prices-round-off)

During the gateway's operation, accuracy of quotes (decimal places) passed for some symbol may change in the external trading system. Decrease in price accuracy at the external trading system's side does not affect the gateway's operation. It still transmits prices with less accuracy. However, if the number of decimal places at the external system's side increases, the gateway starts rounding off the passed prices.

Suppose that the accuracy of quotes has changed from 4 to 5 digits. Obtained five-digit quotes are rounded up by the gateway and used for creating the Market Depth. The round off is always performed in broker's favor. Thus, buy requests of 1.23447, 1.23441 are rounded up to 1.2345, while sell ones of 1.23447, 1.23441 are rounded down to 1.23440.

Changes in symbol price accuracy are recorded in the gateway journal.

<a id="multiaccount"></a>
## Trade Operations Transfer Modes (#multiaccount)

The MetaTrader 5 Euronext FX Gateway allows to send trade operations to Euronext FX using different modes. Client trading orders that are set in MetaTrader 5 platform can be sent to Euronext FX on behalf of the broker's general account (specified in the "Trading login" parameter of the gateway settings) or on behalf of the clients' individual accounts. In the latter case gateway connection to Euronext FX is performed via broker's general account. However, clients' trade operations are transferred to Euronext FX using individual accounts.

  * Order sending mode is controlled by the [Account Mapping Mode (#common)](Euronext-FX.md#common) parameter in the gateway configuration.
  * Trade operations transfer conditions are determined while concluding an agreement between a brokerage company and Euronext FX.
  * In no circumstances it is allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.



If you send trading operations using individual client accounts, the appropriate Euronext FX account number must be specified in each account's settings. This can be done via the [administrator (#trade-accounts)](../../Platform-Setup/Accounts/Editing-Account.md#trade-accounts) or [manager](https://support.metaquotes.net/en/docs/mt5/manager/management/management_accounts/account_view/account_view_account) terminal:

![Client's account in the FastMatch system](images/fastmatch_account.png)

In "Trade accounts" section, select Euronext FX gateway configuration and specify the client's account in the external system. That is the account, on which client's trade operations will be processed in Euronext FX.

Client account numbers are provided by Euronext FX.

```

---

<a id='gateways-fxcm-pro-md'></a>
### 119. `Gateways/FXCM-PRO.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / FXCM PRO

[Previous](LMAX-Global.md) | [Next](Borsa-Istanbul.md)

<a id="metatrader-5-gateway-to-fxcm-pro"></a>
# MetaTrader 5 Gateway to FXCM PRO (#metatrader-5-gateway-to-fxcm-pro)

[FXCM PRO](https://www.fxcmpro.com/) is the institutional arm of FXCM, the largest broker in the United States. FXCM Pro trading system serves 200 000 traders all over the world conducting over 500 000 trades per day with the average daily volume of $14 billion.

FXCM Pro offers brokers the transparent service system based on agency commission with fully anonymous trading. The system provides access to [40 trading symbols](https://www.fxcm.com/uk/markets/) including currency pairs, indices, metals, energy and Treasury bonds. FXCM Pro offers customized pricing for each instrument and account. Based on customer mandate, FXCMs liquidity management team can source the most efficient liquidity providers and partnering venues to match your needs, be it single tickets on large orders, stickier pricing intraday on metals, and much more.

FXCM Pro trading systems (matching engine) are located in New York (Equinix NY7 data center) and Tokyo (Equinix TY3 data center). The system can be accessed both via the Internet and cross connect in FXCM data center.

<a id="two-operation-modes-wholesale-and-liquidity-solutions"></a>
## Two Operation Modes: Wholesale and Liquidity Solutions (#two-operation-modes-wholesale-and-liquidity-solutions)

You can select one of the two operation modes depending on your needs.

Wholesale | Liquidity Solutions  
---|---  
Wholesale is optimal for retail brokers looking to leverage FXCMs scale. Brokers are able to trade in FXCM Pro using large volumes, thus increasing the acceptable volume of non-hedged positions of their traders. Cross Collateralization of FX and CFD Trading All customer positions are netted into one account, allowing for more efficient use of corporate cash. Credit line Through a formal review process FXCM can extend credit in the form of NOP (Net Open Position) in a traditional bank Prime Brokerage manner with flexible settlement terms. No fees on small tickets FXCM provides all currency pairs on offer at 1K ticket sizes with no additional fees. Execution suitable for automated trading FXCMs FX NDD model, and enhanced index and commodity CFD model is ideal for automated traders seeking a better execution experience. | Liquidity Solutions mode provides liquidity for your traders and ability to send their trading operations to FXCM Pro. There are two distinctly different liquidity solutions â trading via a single account in FXCM Core system and trading in FXCM Pro ECN where an individual account is allocated to each trader. FXCM Core This technology suite supports nearly 200 000 traders globally, with over 500 000 trades done daily as well as over $14 billion in daily volumes.

  * NDD execution model is agency based and truly anonymous. Banks and financial institutions comprising FXCMs matching engine have no information about their counterparty. Pending orders are stored on FCXM servers and sent to the matching system only if their execution conditions are fulfilled.
  * Small ticket advantage â FXCM provides all currency pairs on offer at 1K ticket sizes with no additional fees.
  * Multi asset clearing â all assets are traded on one trading account via a single API.

FXCM Pro ECN â institutional API service This technology offers professional and institutional users the ability to tailor pricing on a per instrument, per account basis. Based on customer mandate, FXCMs liquidity management team can source the most efficient liquidity providers and partnering venues to match your needs, be it single tickets on large orders, stickier pricing intraday on metals, and much more. FXCM also provides cross collateralization capabilities for all trading accounts.  
  
<a id="getting-started-with-fxcm-pro"></a>
## Getting Started with FXCM Pro (#getting-started-with-fxcm-pro)

First, connect FXCM Pro to find out the details and conclude an agreement.

Brandon Mulvihill â Global Head, FXCM Pro Direct: +1 646 432 2521 Mobile: +1 917 587 1339 Email: bmulvihill@fxcmpro.com | Chris Hossain â Head of EMEA, FXCM Pro Direct: +44 207 903 6261 Mobile: +44 7 540 789 656 Email: chossain@fxcmpro.com | Siju Daniel â CEO, FXCM Asia Email: sdaniel@fxcm.com | Claudio Flores â VP, API & Systems Trading Email: cflores@fxcm.com  
---|---|---|---  
  
After concluding an agreement, you will receive all necessary data for connecting to FXCM Pro trading system.

> [Order MetaTrader 5 Gateway to FXCM Pro](https://support.metaquotes.net/en/market/product/269)

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

MetaTrader 5 Gateway to FXCM Pro is a separate FXCMProGateway64.exe module that uses the MetaTrader 5 Gateway API for operation. The gateway works via two FIX channels: the first one is for trading, while the second one is for market data.

All orders entered in FCXM Pro are transferred to the unified requests database. The system selects appropriate orders automatically executing opposite orders with matching parameters (symbol, price etc.)

![Gateway operation](images/fxcm_scheme.png)

<a id="market-data"></a>
### Market Data (#market-data)

MetaTrader 5 Gateway to FXCM Pro automatically imports all the necessary symbols and processes their properties. The administrator only needs to perform a primary [setup (#symbols)](FXCM-PRO.md#symbols).

Price data is transmitted in real time. The gateway is capable of narrowing or expanding prices on the go: quotes can be converted according to the settings when passing them to the platform and then re-converted back to their original state when passing trade operations to FXCM Pro. Detailed information on [prices conversion (#markup)](FXCM-PRO.md#markup) is available below.

<a id="trading-operations"></a>
### Trading Operations (#trading-operations)

Orders are sent to MetaTrader 5 Gateway to FXCM Pro for processing in accordance with the set [routing rules (#routing)](FXCM-PRO.md#routing). Processing of requests depends on the type of the order, as well as the gateway configuration.

Order type | Execution  
---|---  
Market order | Delivered directly to FXCM Pro as a market order.  
Take Profit Buy Limit Sell Limit | Depends on [Limit Orders Coverage Mode (#parameters)](FXCM-PRO.md#parameters): Limit Orders Coverage Mode=Gateway (default) Limit orders are processed on FXCM Pro side. Once a limit order has been placed by a client, an appropriate order is sent to FXCM Pro. There it is placed to the general queue awaiting for an opposite request with the same price to appear. Take Profit orders are processed the same way as in the Limit mode. The FXCM Pro system checks the availability of the required amount of funds to cover any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the work is carried out. [Margin reservation (#margin)](FXCM-PRO.md#margin) of the clients should be configured for the appropriate order types in case Limit orders are directly delivered to an external system. By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client. Limit Orders Coverage Mode=Limit Limit Orders and Take Profit orders are processed on the side of the MetaTrader 5. Once a limit order is triggered, an equivalent limit order is sent to FXCM Pro. That order has a short action time specified in Limit Orders Coverage Timeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from FXCM Pro. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5. A limit order with the price equal to a Take Profit level is sent to FXCM Pro at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from FXCM Pro. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on MetaTrader 5 side.   
Limit mode allows to protect against slippage, as a limit order is sent to FXCM Pro system with a specified price rather than a market order for execution by the current price. Limit Orders Coverage Mode=Market Limit orders and Take Profit orders are processed on the MetaTrader 5 platform side. Once they trigger, an appropriate market order is sent to FXCM Pro.  
Buy Stop Sell Stop | Depends on [Stop Orders Coverage (#parameters)](FXCM-PRO.md#parameters): Stop Orders Coverage=Y Delivered directly to FXCM Pro. Similarly to limit orders, margin reservation of the clients should be configured for the appropriate order types on MetaTrader 5 side in case of direct delivery of stop orders to FXCM Pro. Stop Orders Coverage=N Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to the FXCM Pro system.  
Buy Stop Limit Sell Stop Limit | Depends on Stop Orders Coverage: Stop Orders Coverage=Y Delivered directly to FXCM Pro. Similarly to limit orders, margin reservation of the clients should be configured for the appropriate order types on MetaTrader 5 side in case of direct delivery of stop limit orders to FXCM Pro. Stop Orders Coverage=N Processed on the MetaTrader 5 side. Upon order activation, an appropriate limit order is created in MetaTrader 5, and this order is then processed in accordance with the value of the Limit Orders Coverage Mode parameter.  
Stop Loss Stop Out | Processed on the MetaTrader 5 side. Once they trigger, an appropriate market order is sent to FXCM Pro.  
  
> In case connection to  server is lost, the application will try to restore it repeatedly. If pending orders were executed during the disconnection period, they will be updated in the MetaTrader 5 platform after successful reconnection.

<a id="settings"></a>
## Gateway Setup (#settings)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway settings](images/fxcm_common.png)

Set the following parameters on the "Common" tab:

  * ID â unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Module â specify FXCMProGateway64 and accept the default settings after the module selection.
  * Trading server â FXCM Pro server IP-address and the port, where trade requests are processed. This information is provided by FXCM Pro as the SocketConnectHost and SocketConnectPort parameters. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.
  * Trading login â login for connecting the trade flow corresponding to UserName tag (553) in FIX protocol. Provided by FXCM Pro.
  * Password â password for connecting the trade and quote flow corresponding to Password tag (554) in FIX protocol. Provided by FXCM Pro.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The details for connection to the FXCM Pro server where trade requests are processed will be provided during the agreement conclusion.

  
---  
  
Now, go to the "Parameters" tab.

![Gateway parameters setup](images/fxcm_param.png)

Specify the following parameters values here:

  * FIX Trade SenderCompID â standard parameter of the FIX messages heading used for a data sender identification. This parameter is provided by FXCM Pro as the value of SenderCompID (49).
  * FIX Trade TargetCompID â standard parameter of the FIX messages heading used for trading messages recipient identification. This parameter is provided by FXCM Pro as the value of TargetCompID (56).
  * FIX Trade TargetSubID â standard parameter of the FIX messages heading used for trading messages recipient identification. This parameter is provided by FXCM Pro as the value of TargetSubID (57).
  * FIX Market Data Address â IP address and port of the FXCM Pro server, from which market (price) data is transmitted. This information is provided by FXCM Pro as the SocketConnectHost and SocketConnectPort parameters. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.
  * FIX Market Data SenderCompID â standard parameter of the FIX messages heading used for a market data sender identification. This parameter is provided by FXCM Pro as the value of SenderCompID (49).
  * FIX Market Data TargetCompID â standard parameter of the FIX messages heading used for market messages recipient identification. This parameter is provided by FXCM Pro as the value of TargetCompID (56).
  * FIX Market Data TargetSubID â standard parameter of the FIX messages heading used for market messages recipient identification. This parameter is provided by FXCM Pro as the value of TargetSubID (57).
  * FIX Market Data Log Enabled â if Yes, the gateway saves FIX connection (market flow) logs. Enable the parameter only in case of the gateway operation issues. The default value is No.
  * Limit Orders Coverage Mode â mode of processing Limit and Take Profit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:


  *     * Market â Limit and Take Profit orders are processed on the MetaTrader 5 platform side. If an order is activated, an appropriate market order is sent to FXCM Pro.
    * Limit â Limit and Take Profit orders are processed on the MetaTrader 5 side.  
Once a Limit order is triggered, an equivalent Limit order is sent to FXCM Pro. That order has a short action time specified in Limit Orders Coverage Timeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a Limit order with a residual volume will be removed from FXCM Pro. Thus, a client will have a market position as well as a Limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.  
A Limit order with the price equal to a Take Profit level is sent to FXCM Pro at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price â a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a Limit order with a residual volume will be removed from FXCM Pro. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on the MetaTrader 5 side.   
Limit mode allows to protect against slippage, as a Limit order is sent to FXCM Pro system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to FXCM Pro.
    * Gateway â Limit orders are processed on FXCM Pro side. Once a Limit order has been placed by a client, an appropriate order is sent to FXCM Pro. Take Profit orders are processed the same way as in the Limit mode.
  * Limit Orders Coverage Timeout â duration of Limit orders sent to FXCM Pro in Limit mode. Specified in seconds. The default value is 5.
  * Stop Orders Coverage â mode of handling Stop and Stop Limit orders. In case of 'Y' value, these order types will be transferred to FXCM Pro directly. In case of 'N' value, the orders will be processed inside MetaTrader 5 platform until their stop price is reached. After a Stop order is activated, an appropriate market order will be sent to the FXCM Pro system. After a Stop Limit order has been activated, a Limit order is created, which will be processed according to Limit Orders Coverage Mode parameter value.
  * Account Mapping Mode â the gateway supports several [modes of trade operation transferring (#multiaccount)](FXCM-PRO.md#multiaccount) to FXCM PRO: on behalf of the broker's general account and on behalf of the individual accounts used for trading in the MetaTrader 5 platform. Three modes of trades operations transfer are available:
    * omnibus â all orders will be sent to FXCM PRO on behalf of the broker's main account specified in the "Account Mapping" parameter.
    * one-to-one â all orders will be sent to FXCM PRO on behalf of individual accounts on which the orders are placed in MetaTrader 5 (an external system account is specified in the settings of each account).
    * conversion â combination of the previous two modes: orders of the accounts that have specified external system account will be sent on their own behalf, while all other orders will be transferred on behalf of the broker's general account.
  * Account Mapping â the number of the single account in the FXCM PRO system, on behalf of which clients' orders will be sent if the "Account Mapping Mode" parameter is set to "omnibus" or "conversion".
  * Quotes Delay â delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample â the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample â the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample â the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



  * In no circumstances it is allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.
  * Margin reservation of the clients should be configured for the appropriate order types [in case Limit, Stop and/or Stop Limit orders (#margin)](FXCM-PRO.md#margin) are directly transferred to an external system.

  
---  
  
The next stage is to specify the groups of the clients, whose requests will be processed via the MetaTrader 5 Gateway to FXCM Pro, as well as symbols, by which the gateway processes trading operations and broadcasts quotes.

![Configuring groups and symbols](images/fxcm_groups_symbols.png)

Make sure to enable "Allow importing symbol settings" option. The gateway imports symbols from FXCM Pro to Symbols/Preliminary/FXCM directory of the MetaTrader 5 and manages their parameters.

  * Initially, all imported symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After symbols are relocated and trading abilities are enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case, the symbol is not transferred and its trading ability is not turned off.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="margin"></a>
## Margin Setup (#margin)

Margin reservation of the clients should be configured for the appropriate order types in case Limit, Stop and/or Stop Limit orders are directly transferred to an external system.

The external system checks the funds that are necessary to provide any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the work is carried out.

By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client.

After an order has been transferred to the external system, MetaTrader 5 platform is not able to check the client's margin sufficiency any more. After the order has been executed in the external system, the gateway cannot ignore that fact. Therefore, the appropriate trading operation is performed in the platform.

Set non-zero coefficients for the orders directly transferred to the external trading system in symbol settings for the appropriate symbols:

![Margin setup](images/integral_margin_allorders.png)

<a id="routing"></a>
## Configuring Trade Requests Routing (#routing)

Configure the routing to let the clients requests to be transmitted to the FXCM Pro gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

In the screenshots below all orders created by users in the real\fxcm\* groups by symbols from the FXCM\* section will be sent to the gateway for processing.

![Configuring trade requests routing](images/fxcm_routing.png)

After the correct execution of the steps described above, the gateway will be ready for work.

<a id="multiaccount"></a>
## Configuring Trading Accounts (#multiaccount)

MetaTrader 5 GateWay to FXCM PRO allows transferring trading operations to an external system in different modes. The trading orders that are placed by clients in the MetaTrader 5 platform, can be sent to FXCM PRO on behalf of the broker's general account (specified in the [Account Mapping" (#account-mapping)](FXCM-PRO.md#account-mapping) parameter of the gateway settings) or on behalf of the clients' individual accounts. In the latter case, the gateway connects to FXCM PRO via the broker's general account, but clients' trading operations are sent to FXCM PRO using individual accounts.

  * Order transferring mode is controlled by the [Account Mapping Mode (#account-mapping)](FXCM-PRO.md#account-mapping) parameter in the gateway configuration.
  * Trading operations transfer conditions are determined when concluding an agreement between a brokerage company and FXCM PRO.
  * In no case should you change the operation transfer mode during operation. Changing the mode is allowed only when all client positions have been closed.



If you send trading operations using individual client accounts, the appropriate FXCM PRO account number must be specified in each account's settings. This can be done via the [administrator (#trade-accounts)](../../Platform-Setup/Accounts/Editing-Account.md#trade-accounts) or [manager](https://support.metaquotes.net/en/docs/mt5/manager/management/management_accounts/account_view/account_view_account) terminal:

![Client's account in the external trading system](images/fxcm_account.png)

In "Trade accounts" section, select FXCM PRO gateway configuration and specify the client's account in the external system. That is the account, from which client trade operations will be transferred to FXCM PRO.

Client account numbers are provided by FXCM PRO.

<a id="markup"></a>
## Changing Symbols Names and Markups (#markup)

The gateway receives the prices from FXCM PRO and transmits them to clients considering markups. Thus, a brokerage company receives its profit share from each deal performed at FXCM Pro. Markup values are set separately for Bid and Ask prices by each symbol:

![Changing symbol names and price correction](images/fxcm_translation.png)

Besides, you can configure matching of symbol names used in FXCM Pro with the names used in your MetaTrader 5 platform. For example, if the symbol name in FXCM Pro is EURGBPFXCM, and it is called EURGBP in MetaTrader 5, enter EURGBP in the "Symbol" field and EURGBPFXCM in the "Source" field.

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. Below is a schematic example of the conversion:

FXCM Pro | >>> | ask price | EURGBP 0.83004 | >>> | MetaTrader 5 server  
---|---|---|---|---|---  
MetaTrader 5 server | >>> | ask price | EURGBP 0.83006 | >>> | Client terminal  
Client terminal | >>> | buy limit | EURGBP 0.83006 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit | EURGBP 0.83004 | >>> | FXCM Pro  
FXCM Pro | >>> | buy limit execution | EURGBP 0.83004 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit execution | EURGBP 0.83006 | >>> | Client terminal  
  
A broker gains 2 pips of profit in this example. The price is sent to the client terminal only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices submitted by FXCM Pro.

<a id="prices-round-off"></a>
## Prices Round Off (#prices-round-off)

During the gateway's operation, accuracy of quotes (decimal places) passed for some symbol may change in the external trading system. Decrease in price accuracy at the external trading system's side does not affect the gateway's operation. It still transmits prices with less accuracy. However, if the number of decimal places at the external system's side increases, the gateway starts rounding off the passed prices.

Suppose that the accuracy of quotes has changed from 4 to 5 digits. Obtained five-digit quotes are rounded up in a broker's favor. Thus, buy requests of 1.23447, 1.23441 are rounded up to 1.2345, while sell ones of 1.23447, 1.23441 are rounded down to 1.23440.

Changes in symbol price accuracy are recorded in the gateway journal.

<a id="fill-policy-and-order-expiration"></a>
## Fill Policy and Order Expiration (#fill-policy-and-order-expiration)

When sending an order from the MetaTrader 5 client terminal, traders can set the order [execution policy (#fill-policy)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#fill-policy) (FOK, IOC or Return) and [expiration time (#expiration)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#expiration) (Good Till Canceled, Today, Date and Time, Date). In FXCM Pro trading system, the fill policy and expiration are set in a single parameter - Time in Force. Therefore, the gateway performs the following changes when passing the orders:

  * If FOK or IOC fill policy is set for an order, the same policy is applied in FXCM Pro system.
  * If a market order with Return fill policy is placed, it will be passed to FXCM Pro system in Good Till Canceled (GTC) mode.
  * If a limit order with Return fill policy is placed, expiration time from MetaTrader 5 (Good Till Canceled, Today, Specified, Specified Day) is inserted into the appropriate order parameter in FXCM Pro system.
  * If a limit order is activated in MetaTrader 5 platform and the gateway works in the mode of passing limit orders (Limit Orders Coverage Mode = Limit), a limit order with Good Till Date fill time policy is passed to FXCM Pro system. Limit Orders Coverage Timeout parameter also affects the order's lifetime. The gateway removes the placed order upon expiration of the specified time.
  * If a take profit position is activated in MetaTrader 5 platform and the gateway works in the mode of passing limit orders (Limit Orders Coverage Mode = Limit or Limit Orders Coverage Mode = Gateway), a limit order with Good Till Date fill time policy is passed to FXCM Pro system. Limit Orders Coverage Timeout parameter also affects the order's lifetime. The gateway removes the placed order upon expiration of the specified time.



```

---

<a id='gateways-integral-md'></a>
### 119. `Gateways/Integral.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / Integral

[Previous](MetaTrader-4.md) | [Next](Currenex.md)

<a id="metatrader-5-gateway-to-integral"></a>
# MetaTrader 5 Gateway to Integral (#metatrader-5-gateway-to-integral)

MetaTrader 5 Gateway to Integral is a simple, fast and secure integration solution for brokers. The gateway provides liquidity when working in MetaTrader 5. [Integral](https://www.integral.com/) ECN of Integral Development Corp. is one of the largest Electronic Communication Networks allowing to trade commodities. All orders entered in ECN are transferred to the unified requests database. The system selects appropriate orders automatically executing opposite orders with matching parameters (symbol, price etc.)

About Integral

Founded in 1993, [Integral Development Corp.](https://www.integral.com/) offers Integral multi-sided trading network (ECN, Electronic Communication Network) for foreign exchange. Integral technology unites various Forex market participants into the single trading network. Direct access to interbank liquidity via STP (Straight Through Processing) technology allows to maximize the speed of the participants orders execution. ECN Integral combines the liquidity of such financial institutions, as Citibank, Deutsche Bank, Bank of America, UBS, HSBC, NOMURA, RBS, BNP Paribas and many others.

Integral allows to trade more than 100 financial instruments including major currency pairs, cross rates, exotic currencies and precious metals.

<a id="necessary-actions-for-working-with-integral"></a>
## Necessary Actions for Working with Integral (#necessary-actions-for-working-with-integral)

To be able to provide trading services using Integral, a brokerage company must first contact Integral Development Corp. for concluding the agreement. Select the closest Integral office:

  * +1 (212) 252-2243 (North America),
  * +44 203 514-2439 (UK, the EMEA region),
  * +65 3158 0800 (Asia, Singapore)
  * +852 80 903 855 (Hong Kong),
  * +813 3242 6170 (Japan)



Or send an email to [support@integral.com](mailto:support@integral.com).

Further information can be requested on the official Integral website via a [special form](https://www.integral.com/contact/). After conclusion of an agreement, you will receive all necessary data for connection to the Integral server.

> [Order MetaTrader 5 Gateway to Integral](https://support.metaquotes.net/en/market/product/264)

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

MetaTrader 5 Gateway to Integral is a separate IntegralGateway64.exe module that uses the MetaTrader 5 Gateway API for operation.

The foundation of Integral's FX solutions is the FX Grid, a global inter-institutional connectivity and trading network, linking market making banks to Forex market participants. To connect to that network, the gateway uses FX Inside API, which is a special set of interfaces provided by Integral for direct access to FX Grid. The gateway operates as a mediator between two systems connecting Integral and MetaTrader 5 platform. All data between the Integral system and the gateway is transmitted using FIX protocol over the encrypted connection. The gateway sends encrypted FIX messages and returns them to the MetaTrader 5 platform using the MetaTrader 5 Gateway API.

![How the Gateway Works](images/integral_scheme.png)

<a id="market-data"></a>
### Market Data (#market-data)

MetaTrader 5 Integral Gateway automatically imports all the necessary symbols and processes their properties. An administrator only needs to perform primary setup.

Price data is transmitted in real time. The gateway can narrow or widen prices: convert quotes in accordance according with the settings when sending them to the platform, and then perform the inverse conversion to the original state when sending trading operations to Integral. Detailed information on prices correction is available below.

<a id="trading-operations"></a>
### Trading Operations (#trading-operations)

Orders are sent the the MetaTrader 5 Gateway to Integral in accordance with the configured routing rules. Processing of requests depends on the type of the order, as well as in the gateway configuration.

Order type | Execution  
---|---  
Market Order | Delivered directly to Integral as a market order.  
Take Profit Buy Limit Sell Limit | Depends on Limit Orders Coverage: Limit Orders Coverage Mode=Gateway (default) Limit orders are processed on the side of Integral. Once a limit order has been placed by a client, an appropriate order is sent to Integral. Take Profit orders are processed the same way as in the Limit mode. The Integral system checks the availability of the required amount of funds to cover any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out. Margin reservation of the clients should be configured for the appropriate order types in case Limit orders are directly delivered to an external system. By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client. Limit Orders Coverage Mode=Limit Limit Orders and Take Profit orders are processed on the side of the MetaTrader 5. Once a limit order is triggered, an equivalent limit order is sent to Integral. That order has a short action time specified in Limit Orders Coverage Timeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Integral. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5. A limit order with the price equal to a Take Profit level is sent to Integral at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Integral. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on MetaTrader 5 side.   
Limit mode allows to protect against slippage, as a limit order is sent to Integral system with a specified price rather than a market order for execution by the current price. Limit Orders Coverage Mode=Market Limit orders and Take Profit orders are processed on the MetaTrader 5 platform side. Once they trigger, an appropriate market order us sent to Integral.  
Buy Stop Sell Stop | Depends on Stop Orders Coverage: Stop Orders Coverage=Y Delivered directly to Integral. Like with limit orders, margin reservation of the clients should also be configured for the appropriate order types on the MetaTrader 5 side in case Stop orders are directly delivered to Integral. Stop Orders Coverage=N Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to Integral system.  
Buy Stop Limit Sell Stop Limit | Depends on Stop Orders Coverage: Stop Orders Coverage=Y Delivered directly to Integral. Like with limit orders, margin reservation of the clients should also be configured for the appropriate order types on the MetaTrader 5 side in case Stop-Limit orders are directly delivered to Integral. Stop Orders Coverage=N Processed on the MetaTrader 5 side. Upon order order activation, an appropriate limit order is created in MetaTrader 5, and this order is then processed in accordance with the value of the Limit Orders Coverage Mode parameter.  
Stop Loss Stop Out | Processed on the MetaTrader 5 side. Once they trigger, an appropriate market order us sent to Integral.  
  
  * In case connection to Integral server is lost, the application will try to restore it repeatedly. In case pending orders have been executed at that, they will be updated in the MetaTrader 5 platform after connection is restored.
  * The Integral system allows a broker to cancel orders in case of connection loss. Integral system does not cancel orders by default in that case but, nevertheless, you should notify the Integral technical support about the necessity to disable that option for your account (pending orders should not be deleted in case of connection loss).

  
---  
  
<a id="settings"></a>
## Gateway Setup (#settings)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway Settings](images/integral_common.png)

Set the following parameters on the "Common" tab:

  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Module — specify IntegralGateway64 and accept the default settings after the module selection.
  * Trading server — Integral server IP-address and the port, where trade requests are processed. This information is provided by Integral.
  * Trading login — Integral server connection login (equal to SenderCompID).
  * Password — password for connection to the Integral server (equal to SenderCompPasswd).



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The details for connection to the Integral server, where trade requests are processed, are provided during the agreement conclusion.

  
---  
  
Other parameters are set similarly to other gateways. Default values are used in most cases.

Now, go to the "Parameters" tab.

![Gateway parameters setup](images/integral_param.png)

Specify the following parameters values here:

  * FIX TargetCompID — a standard parameter of the FIX messages heading used for trading messages recipient identification. This parameter is provided by Integral as the value of TargetCompID.
  * FIX SenderSubID — a standard parameter of the FIX messages heading used for a trading participant (a legal entity) identification. Provided by Integral as the value of FIX_SenderSubID.
  * FIX SenderCompID — a standard parameter of the FIX messages heading used for a data sender identification. Provided by Integral as the value of senderCompID without the 'quote' or 'trader' prefixes. For example, if Integral has submitted to you sendercompID = quote.9898AKD.10, the value 9898AKD.10 should be used for FIX SenderCompID parameter.
  * FIX Trade OnBehalfOfCompID — is a standard parameter of the FIX messages heading used for a trade participant identification. Provided by Integral as the value of OnBehalfOfCompID. If the parameter value is specified, the getaway will additionally fill the OnBehalfOfCompID (115) tag in outgoing messages of the trading channel. An optional parameter.
  * FIX Trade Account Number Set — if you set "Yes" for this parameter, the gateway will additionally fill the OnBehalfOfSubID (116) tag in all outgoing FIX messages. The MetaTrader 5 login of the client who performed this operation is written in this tag. When default No is used, the tag is not filled.
  * FIX Trade Capture Address — IP address and port of the Trade Capture server, provided by Integral. The gateway uses a separate FIX connection to the Trade Capture (Drop Copy) Exchange service. This connection is used by the gateway to receive the stream of deals performed through other terminals (not MetaTrader 5). If this parameter is not filled, the gateway will not connect to Trade Capture and will only work with the trading/quoting server of the exchange.
  * FIX Trade Capture Username — login for connection to the Trade Capture server.
  * FIX Trade Capture Password — password for connection to the Trade Capture server.
  * FIX Trade Capture TargetCompID — FIX messages heading standard parameter used for trading messages recipient identification. The parameter is provided by Integral as the TargetCompID value.
  * FIX Trade Capture SenderCompID — FIX messages heading standard parameter used for a data sender identification. Provided by Integral as the value of senderCompID without 'quote' or 'trader' prefixes.
  * FIX Trade Capture SenderSubID — FIX messages header standard parameter used for a trading participant (a legal entity) identification. Provided by Integral as the value of FIX_SenderSubID.
  * FIX Trade Capture Login MT — account number on the MetaTrader 5 platform side, to which all deals from Trade Capture will be transmitted.
  * FIX Trade Capture Stop Out Enabled — allow closing of positions upon reaching [Stop Out (#stopout)](../../Platform-Setup/Groups/Group-Settings.md#stopout). If set to "No" (default), positions opened via the gateway will not be closed automatically, if Stop Out is reached on the trading platform side. If a position is opened with FIX Trade Capture Stop Out Enabled = Yes, then closing by Stop Out can occur even if you change the parameter value to "No". It is only guaranteed that the ban to close will be effective for positions opened after changing the parameter value to "No".
  * FIX Trade Spread Set — transmit information about [the spread difference values in the trader group](../../Platform-Setup/Groups/Group-Symbol-Settings/Common.md) to Integral. Such information can be required by the exchange. If set to "No" (default), this data is not transmitted. If set to "Yes", the gateway will transmit the current spread value in tag 7547 for each request. For market orders, the current symbol price will be additionally provided in tag 44.
  * FIX Market Data Address — IP address and port of the Integral server, from which the quotes are provided. By default, the gateways receives information about trading requests and price data from one server, which is specified in the "Trade server" field. By using the FIX Market Data Address parameter, you can configure the gateway to receive quotes in a separate stream. To connect to the quoting server you should use the same login and password, which are used for the trade request processing server.
  * FIX Market Data Log Enabled — if "YES" is set, the gateway will save to disk the full quoting connection log. This can be useful in operation debugging. The log is not saved by default (value "No").
  * FIX Market Data DeliverToCompID — indicates liquidity provider from which quotes should be requested. If the parameter is set, the specified value will be added to the DeliverToCompID (128) tag of FIX messages of the quoting session subscription. If the parameter is not set, "All" will be used for the DeliverToCompID tag, which means subscription to quotes from all available liquidity providers.
  * Limit Orders Coverage Mode — the mode of processing of Limit and Take Profit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:
    * Market — limit and Take Profit orders are processed on the MetaTrader 5 platform side. An appropriate market order is sent to Integral after an order has been triggered.
    * Limit — limit and Take Profit orders are processed on the MetaTrader 5 side.  
Once a limit order is triggered, an equivalent limit order is sent to Integral. That order has a short action time specified in Limit Orders Coverage ModeTimeout parameter. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Integral. Thus, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.  
A limit order with the price equal to a Take Profit level is sent to Integral at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price — a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. Thanks to a short expiration time, a limit order with a residual volume will be removed from Integral. Therefore, a client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on the MetaTrader 5 side.  
Limit mode allows to protect against slippage, as a limit order is sent to Integral system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to Integral.
    * Gateway — limit orders are processed on the Integral side. Once a limit order has been placed by a client, an appropriate order is sent to Integral. Take Profit orders are processed the same way as in the Limit mode.
  * Stop Orders Coverage — Stop and Stop Limit order processing mode. In case of 'Y' value these order types will be delivered to Integral directly. In case of 'N' value the orders will be processed inside MetaTrader 5 platform until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to Integral system. After a stop limit order has been activated, a limit order is created, which will be processed according to Limit Orders Coverage Mode parameter value.
  * Limit Orders Coverage Timeout — expiry of Limit Orders that are sent to Integral in the Limit mode. Specified in seconds. The default value is 5.
  * Week Time Begin — gateway operation start time on Sunday. The value is specified in HH:MM format for Eastern Standard Time (EST). For example, 2:00.
  * Week Time End — gateway operation end time in Friday. The value is specified in HH:MM format for Eastern Standard Time (EST). For example, 23:00.


  * Weekend Trading Enabled — allow the gateway to trade on weekends. The default value is "No", which means that trading begins on Sunday at "Week Time Begin" and ends on Friday at "Week Time End". If set to "Yes", the gateway will operate from "Week Time Begin" on Sunday until "Week Time End" on the next Sunday. To keep the gateway running 24/7, enable "Weekend Trading Enabled" and set "Week Time Begin" to a time earlier than "Week Time End".


  * Min Quantity Set — enables/disables [minimum volume (#volumes)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#volumes) checks for symbols when executing orders in Integral. The default "No" value instructs Integral to execute orders using deals of any size. The "Yes" value informs Integral that orders can be filled using deals with the volume no less than the "Minimum volume" parameter in symbol settings on the trading platform side.
  * Slippage Allowable — maximum allowable slippage for market orders. The parameter corresponds to tag 211 in the FIX protocol. The default value is 0, i.e. no tag is passed.
  * Orders Full Fill Only — enables/disables the filling of tag 110 in the FIX protocol when forwarding all orders. The tag sets the minimum volume (equal to the requested volume) in which the order can be executed. The flag ensures the correct implementation of the Fill or Kill execution. Supported values are "Yes" and "No" (default).
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



  * In no circumstances it is allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.
  * When Limit, Stop and/or Stop Limit orders are directly delivered to an external system, margin reservation of the clients should be configured for the appropriate order types.

  
---  
  
The next stage is to specify the groups of the clients, whose requests will be processed via the MetaTrader 5 Integral Gateway. All groups are configured on the screenshot below, but you can configure groups according to your business logic.

![Configuration of groups](images/integral_group.png)

Then configure the list of symbols, according to which the gateway will process trade operations and feed quotes.

![Configuring the symbols](images/integral_symbols.png)

Make sure to enable "Allow importing symbol settings" option. The symbols available to Integral will be imported to Symbols/Preliminary/Integral directory of the MetaTrader 5 platform. Besides, that will allow the gateway to manage the settings of the symbols used in trading via Integral.

  * The symbols imported by the gateway are put to the "\Preliminary" symbols subgroup. All symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After symbols are relocated and trading abilities are enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case the symbol is not transferred and its trading ability is not turned off.
  * In case some changes are implemented to the Depth of Market parameter of the symbol settings, Integral gateway and a history server must be restarted to let the changes take effect. In fact, restart is required after any change in the symbol settings.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="margin"></a>
## Margin Setup (#margin)

Margin reservation of the clients should be configured for the appropriate order types in case Limit, Stop and/or Stop Limit orders are directly transferred to an external system.

The external system checks sufficiency of the funds that are necessary to provide any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the operation is carried out.

By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client.

After an order has been transferred to the external system, MetaTrader 5 platform is not able to check the client's margin sufficiency any more. After the order has been executed in the external system, the gateway cannot ignore that fact. Therefore, the appropriate trading operation is performed in the platform.

Set non-zero coefficients for the orders directly transferred to the external trading system in symbol settings for the appropriate symbols to configure margin collection:

![Margin Setup](images/integral_margin_allorders_1.png)

<a id="routing"></a>
## Configuring trade requests routing (#routing)

Configure the routing to let the clients requests to be transmitted to the Integral gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

In the figure below all client orders created by users in the demo\demoforex group having symbols from Integral\ group will be sent to the gateway for processing.

![Configuring routing](images/integral_routing.png)

After the correct execution of the steps described above, the gateway will be ready for work.

<a id="markup"></a>
## Changing symbols names and prices correction (#markup)

MetaTrader 5 Gateway to Integral feeds the price flow from an external trading system to the MetaTrader 5 platform and controls settings of appropriate symbols. In addition, the gateway allows you to edit quotes and Market Depth data transmitted to clients from an external system.

The gateway receives prices from Integral and delivers them to clients taking into account conversion settings. Clients perform trading operations using converted prices. However, while processing trading operations on the gateway and their transmission to Integral, initial, not converted prices are automatically used.

Thus, by increasing the selling price and reducing the purchase price ("price spreading") a brokerage company receives its profit share from each deal performed at Integral. The correction value is set separately for each symbol on the "Translations" tab:

![Configuring Conversion](images/integral_tranlsation.png)

Here you can configure matching of symbol names used in Integral with the names used in your MetaTrader 5 platform. For example, if the symbol name in Integral is EURGBPINT, and it is called EURGBP in the MetaTrader 5, enter EURGBP in the "Symbol" field and EURGBPINT in the "Source" field.

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. Below is a schematic example of the conversion:

Integral | >>> | ask price | EURGBP 0.83004 | >>> | MetaTrader 5 server  
---|---|---|---|---|---  
MetaTrader 5 server | >>> | ask price | EURGBP 0.83006 | >>> | Client terminal  
Client terminal | >>> | buy limit | EURGBP 0.83006 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit | EURGBP 0.83004 | >>> | Integral  
Integral | >>> | buy limit execution | EURGBP 0.83004 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit execution | EURGBP 0.83006 | >>> | Client terminal  
  
A broker gains 2 pips of profit in this example. The price is sent to the client terminal only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices submitted by Integral.

<a id="prices-round-off"></a>
## Prices Round Off (#prices-round-off)

During the gateway's operation, accuracy of quotes (decimal places) passed for some symbol may change in the external trading system. Decrease in price accuracy at the external trading system's side does not affect the gateway's operation. It still transmits prices with less accuracy. However, if the number of decimal places at the external system's side increases, the gateway starts rounding off the passed prices.

Suppose that the accuracy of quotes has changed from 4 to 5 digits. Obtained five-digit quotes are rounded up by the gateway and used for creating the Market Depth. The round off is always performed in broker's favor. Thus, buy requests of 1.23447, 1.23441 are rounded up to 1.2345, while sell ones of 1.23447, 1.23441 are rounded down to 1.23440.

Changes in symbol price accuracy are recorded in the gateway journal.

<a id="fill-policy-and-order-expiration"></a>
## Fill Policy and Order Expiration (#fill-policy-and-order-expiration)

While sending an order from the MetaTrader 5 client terminal, the trader can additionally specify the [Fill Policy (#fill-policy)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#fill-policy) (FOK, IOC or Return) and [expiry (#expiration)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#expiration) of the order (Good till canceled, Today, Date and time, Time). In the Integral trading system, the fill policy and expiration are set in a single parameter - Time in Force. The gateway performs the appropriate changes when sending orders:

  * If FOK or IOC fill policy is set for an order, the same policy is applied in Integral system.
  * If a market order with Return fill policy is placed, it will be passed to Integral system in Good Till Canceled (GTC) mode.
  * If a limit order with Return fill policy is placed, expiration time from MetaTrader 5 (Good Till Canceled, Today, Specified, Specified Day) is inserted into the appropriate order parameter in Integral system.
  * If a limit order is activated in MetaTrader 5 platform and the gateway works in the mode of passing limit orders (Limit Orders Coverage Mode = Limit), a limit order with Good Till Date fill time policy is passed to Integral system. Limit Orders Coverage Timeout parameter also affects the order's lifetime. The gateway removes the placed order upon expiration of the specified time.
  * If a take profit position is activated in MetaTrader 5 platform and the gateway works in the mode of passing limit orders (Limit Orders Coverage Mode = Limit or Limit Orders Coverage Mode = Gateway), a limit order with Good Till Date fill time policy is passed to Integral system. Limit Orders Coverage Timeout parameter also affects the order's lifetime. The gateway removes the placed order upon expiration of the specified time.



```

---

<a id='gateways-interactive-brokers-md'></a>
### 119. `Gateways/Interactive-Brokers.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / Interactive Brokers

[Previous](Borsa-Istanbul.md) | [Next](../WebTerminal.md)

<a id="metatrader-5-gateway-to-interactive-brokers"></a>
# MetaTrader 5 Gateway to Interactive Brokers (#metatrader-5-gateway-to-interactive-brokers)

[Interactive Brokers](https://www.interactivebrokers.com) provides trading access to the largest Exchanges in Americas, Europe, Africa and Asia-Pacific region. One account features access to 125 markets in 31 countries, including NASDAQ, NYSE, CHX, MSE and LSE, among others. With Interactive Brokers, you can offer multi-asset trading to your traders: stocks, options, futures, currencies, ETF and CFD.

Using the MetaTrader 5 Gateway to Interactive Brokers, the integration can be performed with the minimum investment of time and money. The gateway launch requires only a few steps:

  * [Open an account with Interactive Brokers (#open-account)](https://www.interactivebrokers.co.uk/inv/en/main.php#open-account)
  * [Purchase a gateway from the App Store](https://support.metaquotes.net/en/market/product/412) (temporarily not available for purchasing)
  * Perform a simple gateway configuration
  * Specify appropriate Interactive Brokers accounts in MetaTrader 5 trading accounts



After that, your traders will be able to trade on the largest global exchanges using the MetaTrader 5 desktop, mobile and web terminals. You do not need to set up trading for each market and each instrument separately. The gateway automatically controls settings of all symbols.

> [Request MetaTrader 5 Gateway to Interactive Brokers](https://support.metaquotes.net/en/market)

<a id="how-the-gateway-operates"></a>
## How the Gateway operates (#how-the-gateway-operates)

MetaTrader 5 Gateway to Interactive Brokers is a separate InteractiveBrokersGateway64.exe module which operates using the MetaTrader 5 Gateway API. To connect to a trading system, the gateway uses an interlayer, which can be the IB Gateway or The Trader Workstation (TWS) application provided by Interactive Brokers. Please see below for details.

Trading operations are forwarded via the gateway in accordance with the routing rules. Request processing depends on the order type:

Order Type | Execution  
---|---  
Market Order | Forwarded directly to the Interactive Brokers system as a market order.  
Buy Limit Sell Limit | Forwarded directly to the Interactive Brokers system as a limit order.  
Buy Stop Sell Stop | Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order is sent to the Interactive Brokers system.  
Buy Stop Limit Sell Stop Limit | Processed on the MetaTrader 5 side. Upon activation in MetaTrader 5, an appropriate limit order is sent to the Interactive Brokers system.  
Take Profit | Processed on the MetaTrader 5 side. Upon activation in MetaTrader 5, a limit order with the Take Profit activation price is sent to the Interactive Brokers system.  
Stop Loss | Processed on the MetaTrader 5 side. Upon activation, an appropriate market order is forwarded to the Interactive Brokers system.  
Stop Out | Processed on the MetaTrader 5 side. Upon activation, market orders to close all client's positions are sent to the Interactive Brokers system.  
  
The following parameters are supported by the gateway:

  * Trading server — address and port for connection to IB Gateway or TWS.
  * Login and Password — authorization data for logging into the Interactive Brokers system.
  * Trading Mode — account type at Interactive Brokers.
  * Start IBGateway — IB Gateway application launch mode when started by the gateway.
  * Command Port — port for managing IB Gateway.
  * Client ID — identifier of connection to IB Gateway.
  * Import Default Symbols — mode of operation with trading instruments.
  * Rate Limit — allowable frequency of requests, sent by the gateway.
  * Flex Request Token — token to request deals history.
  * Flex Request Query — report template to request deals history.



Detailed descriptions of each of the parameters are available at the links.

<a id="connect"></a>
## Connection to Interactive Brokers (#connect)

Firstly, you need access to the Interactive Brokers trading system. Please contact the company through their official website <https://www.interactivebrokers.com>. If you already have the system login and password, this step can be skipped.

API Interactive Brokers runs as an interface to their trading applications [IB Gateway](https://www.interactivebrokers.com/en/index.php?f=5041) and [The Trader Workstation](https://www.interactivebrokers.com/en/index.php?f=5041) (TWS). These are two different applications: TWS is a full-fledged trading terminal with a graphical interface, while IB Gateway is a simplified windows application specifically designed for integration with other systems. 

The MetaTrader 5 gateway also operates through these applications. The gateway can either connect to installed applications or it can deploy IB Gateway on a local computer, if an appropriate application is not found.

IB Gateway and TWS have some differences in terms of interaction with the gateway. We strongly recommend using IB Gateway, because it supports all of the available Interactive Brokers API features.

<a id="connection-with-a-local-application-launch"></a>
### Connection with a local application launch (#connection-with-a-local-application-launch)

By default, the gateway searches for an installed IB Gateway of a compatible version on the local server and launches it in automatic mode, so there is no need to authenticate manually and to confirm warnings by the operator. If an appropriate IB Gateway installation is not found, the gateway will download and install it.

To launch the gateway in this mode, set up the following parameters in the gateway [configuration](../../Platform-Setup/Gateways/Configuration-of.md):

![Configuring the gateway to operate with the local IB Gateway](images/ib_gateway_param_local.png)

In the "Common" section:

  * Trading server — address 127.0.0.1 and port, which will be used by the gateway to establish an API-connection with IB Gateway. The gateway receives and sends data at this address. Address and port must be separated by a colon. Any free system port can be used. The default is 127.0.0.1:4002.
  * Trading login — user name for authorization in the Interactive Brokers system via IB Gateway.
  * Password — password for authorization.



In the "Parameters" section:

  * Trading Mode — your Interactive Brokers account type. Can be 'live' or ['paper'](https://www.interactivebrokers.com/en/software/omnibrokers/topics/papertrader.htm).
  * Start IBGateway — IB Gateway or TWS operation mode. To enable automatic IB Gateway launch by the gateway, set "Yes" (default). If the appropriate application is not found, the gateway will automatically deploy IB Gateway and will connect to it.
  * Command Port — command port via which connection to control IB Gateway will be established. Any free system port can be used. The default port is 7462.
  * Client ID — identifier of client API connection with which the gateway will connect to IB Gateway. You can use any value from 0 to 31. If several clients connect to one IB Gateway, you should ensure their Client IDs are unique. Value 0 is used by default.



To enable the gateway to connect IB Gateway to Interactive Brokers servers, please disable the two-factor authentication in your account settings. This can be done [in your personal account on the Interactive Brokers site](https://www.interactivebrokers.co.uk/sso/Login?RL=1). Navigate to Settings — User Settings — Secure Login System.

![Disabling two-factor authentication for the account](images/ib_gateway_twostep_disable.png)

Click the gear icon next to "Secure Login required for trading". If this section is not available, please contact the Interactive Brokers technical support. Then select "I only want to use my Secure Login Device when logging into Account Management".

![Disabling two-factor authentication for the account](images/ib_gateway_twostep_disable-login.png)

<a id="connection-without-local-application-launch"></a>
### Connection without local application launch (#connection-without-local-application-launch)

If for any reason you need to start IB Gateway (or TWS) manually, set the following parameters in the gateway configuration:

  * Trading server — address and port, which will be used by the gateway to establish an API-connection with IB Gateway, separated with a colon. The port must be previously specified in application settings.
  * Client ID — identifier of client API connection with which the gateway will connect to IB Gateway (or TWS). You can use any value from 0 to 31. If several clients connect to one IB Gateway, you should ensure their Client IDs are unique. Value 0 is used by default.
  * Start IBGateway — set "No", for the gateway to use connection to a remote IB Gateway (or TWS).



The port on which IB Gateway listens to incoming connections from the gateway should be configured under 'Configure' — 'Settings':

![Configuring port for IB Gateway](images/ib_gateway_ibgateway_port.png)

The port on which TWS listens to incoming connections from the gateway should be configured under 'Files' — 'Global Configuration':

![Configuring port for TWS](images/ib_gateway_tws_port.png)

Any free system port can be used. Also it is necessary to disable the "Read-Only API" option in this section.

<a id="symbols"></a>
## Configuring financial instruments (#symbols)

Interactive Brokers provides access to a [variety of trading exchanges](https://www.interactivebrokers.co.uk/en/index.php?f=45165). Please visit the company's website for the [full list of trading symbols](https://www.interactivebrokers.co.uk/en/index.php?f=45167). API Interactive Brokers does not provide the ability to automatically download all available trading instruments, therefore, work with symbols can be organized in two ways:

<a id="built-in-list-of-symbols"></a>
### Built-in list of symbols (#built-in-list-of-symbols)

You can use the built-in list of symbols, which was created based on publicly available data provided by exchanges. This is the default method used in the gateway.

At start, the gateway creates the file [history server directory]\Gateway\IBGateway\<Gateway configuration name>\bases\instruments.csv with a predefined list of financial instruments. By default, the list contains symbols from the three most popular exchanges: NYSE, NASDAQ and AMEX. The file can be edited, and thus new symbols can be added or unused instruments can be deleted from it. According to this list, the gateway requests symbol specifications on the Interactive Brokers side and imports them to the trading platform, into InteractiveBrokers\<Exchange> symbol groups.

To enable this mode, allow the gateway access to the appropriate group of symbols on the trading platform side. Add it to the ["Symbol" section of the gateway settings (#symbols)](../../Platform-Setup/Gateways/Configuration-of.md#symbols):

![Setting access to trading platform symbols for the gateway](images/ib_gateway_symbols.png)

Also, make sure to enable "Allow importing symbol settings" option.

Each symbol description is contained in the instruments.csv file. Each symbol description starts with a new line and has the following format: "<Symbol>,<Type>,<Exchange>". The following values can be used for the instrument type:

  * STK — stock or ETF
  * OPT — option
  * FUT — futures
  * IND — index
  * FOP — futures option
  * CASH — Forex
  * BAG — combo
  * WAR — warrant
  * BOND — bond
  * CMDTY — commodity
  * FUND — mutual fund



Example of instruments.csv contents:

AAPL,STK,NASDAQ   
MSFT,STK,NASDAQ   
MSFT,STK,MEXI   
LE,FUT,GLOBEX   
ES,FUT,GLOBEX   
NQ,FUT,GLOBEX   
EUR,FUT,GLOBEX   
GBL,FUT,DTB   
DAX,FUT,DTB   
EUR.USD,CASH,IDEALPRO   
ES,FUT,GLOBEX,201912   
ES,FOP,GLOBEX,201912  
---  
  
This file can be edited and thus you can add new symbols or delete unused ones.

A symbol name used by Interactive Brokers can differ from its traditional name used on the exchange. The same applies to the exchange name. To check symbol and exchange names, please visit the Interactive Brokers website, section [Product Listings](https://www.interactivebrokers.co.uk/en/index.php?f=45167). For example, to find Microsoft stocks traded on the NASDAQ exchange, perform the following:

1\. Select the NASDAQ exchange (NASDAQ) from the list:

![Find the exchange in the Product Listings sections](images/ib_gateway_search_exchange.png)

2\. Find the company name by specifying Microsoft in the search bar and find the symbol name in the table. Next, open the page with the detailed symbol description: it features the names of the exchange in which the instrument is traded:

![Find the instrument and the exchanges in which the symbol is traded](images/ib_gateway_search_exchange2.png)

In this example, the MSFT security is traded on five exchanges: NASDAQ, CHX, IEX, NMS, NYSE, however the main exchange is the one marked in bold, i.e. NASDAQ. Thus, the following should be specified in file instruments.csv: MSFT,STK,NASDAQ.

<a id="creating-symbols-manually"></a>
### Creating symbols manually (#creating-symbols-manually)

Instead of using the built-in list, you can create your own list of required sybmols. You only need to create a configuration with proper naming and leave default settings. Using the platform list, the gateway will request appropriate configurations from Interactive Brokers and will update them if the symbol is found.

We recommend creating all symbols in a separate subcategory, for example InteractiveBrokers. This will enable efficient control of traders' access to liquidity using [group settings (#symbols)](../../Platform-Setup/Groups/Group-Settings.md#symbols). All symbols should be named according to the following rule: <Symbol>.<Exchange>. For example, AAPL.NASDAQ, MSFT.MEXI etc.

After creating all required symbols allow the gateway access to them. This can be done by adding the relevant symbol category to the ["Symbols" section under gateway settings (#symbols)](../../Platform-Setup/Gateways/Configuration-of.md#symbols):

![Setting access to trading platform symbols for the gateway](images/ib_gateway_symbols_1.png)

Also, make sure to enable "Allow importing symbol settings" option.

The gateway will regularly (at least once a day) request symbol specifications on the Interactive Brokers side and, if necessary, update settings for these symbols in the MetaTrader 5 platform. If any of the symbols is not available for trading in InteractiveBrokers, the gateway will move it to the InteractiveBrokers\Deleted group.

To prevent the gateway from using the built-in list of symbols, set "No" for the parameter "Import Default Symbols".

![Disabling default import of symbols](images/ib_gateway_param_import.png)

<a id="history"></a>
## Obtaining the history of trades (#history)

One of the main gateway purposes is to ensure a complete and correct trading history for each account on the MetaTrader 5 side. This is also required for a proper calculation of current open positions.

The gateway transmits all executed deals to the platform in real time. This includes results of operations requested directly from the platform as well as deals executed via other clients (for example, TWS). If the gateway is stopped for some time, it will need to retrieve from Interactive Brokers the history of all deals which were performed within this period. The gateway has two mechanisms, which are used depending on the downtime duration:

  * If the gateway was stops for no more than one trading day, the history of deals for the current trading day is requested.
  * When the gateway was down for a longer period, the history for the last year is requested.



No additional setup is required for requesting the last day deals, while the gateway can automatically retrieve them if necessary. The history of deals for the last year is requested from special Flex reports provided by Interactive Brokers. To enable access to the reports, you should set up a template and receive a token via a personal account.

> The history of deals can only be obtained when connected via IB Gateway. This functionality is not supported for TWS.

<a id="flex-token"></a>
### Creating a Flex Token (#flex-token)

Go to your [personal account on the Interactive Brokers website](https://www.interactivebrokers.co.uk/sso/Login?RL=1) and select Settings — Account Settings section from the main menu. Then click the gear icon next to the Flex Web Service:

![Creating a Flex Token](images/ib_gateway_flex_token.png)

The "Configure Flex Web Service" window will open. Check the box next to "Flex Web Service Status" and click "GENERATE NEW TOKEN":

![Creating a Flex Token](images/ib_gateway_flex_token2.png)

In the next step, select the token validity period of 1 year and click "GENERATE NEW TOKEN". Specify the the generated token in the "Flex Request Token" gateway parameter.

![Specify the generated token in gateway settings.](images/ib_gateway_flex_token3.png)

> When the token expires, generate a new one and update the corresponding gateway parameter.

<a id="flex-report"></a>
### Creating a Flex Report template (#flex-report)

Open the menu in your personal account and go to the Reports — Tax Docs section:

![Go to Reports — Tax Docs](images/ib_gateway_flex_report_tax_docs.png)

Add a new report on the "Flex Queries" tab. Click the plus icon in the "Activity Flex Query" section:

![Add a new report in the "Activity Flex Query" section](images/ib_gateway_flex_report_query_add.png)

Specify the desired name for the report, and then select "Trades" under Sections.

![Set the report name and go to field selection](images/ib_gateway_flex_report_create.png)

In the next window, select "Executions" and the following fields:

  * AccountID
  * Symbol
  * Currency
  * Conid
  * Date/Time
  * ListingEchange
  * Exchange
  * TradeID
  * IBExecutionID
  * Quantity
  * TradePrice
  * IbCommission



![Select required fields for the report](images/ib_gateway_flex_report_columns.png)

Then click "Save". Select the following options under the "Delivery Configuration" section:

  * Accounts — all accounts in Interactive Brokers which are available to the gateway
  * Models — Optional
  * Format — XML
  * Period — Last 365 Calendar Days



![Configure the "Delivery Configuration" section](images/ib_gateway_flex_report_delivery.png)

Set the required data format under the "General Configuration" section:

  * DateFormat — yyyMMdd
  * TimeFormat — HH:mm:ss
  * Date/Time Separator — single-space



![Configure "General Configuration"](images/ib_gateway_flex_report_general.png)

Then click "Continue". Continue settings in the next window and click "Create".

![Complete report creation by confirming the settings](images/ib_gateway_flex_report_confirm.png)

You can find out the new report ID by clicking on the edit button:

![Go to report editing](images/ib_gateway_flex_report_edit.png)

The report ID will be shown in the upper part of the window. Copy this text.

![Copy the report ID](images/ib_gateway_flex_report_id.png)

Paste this ID as value of the "Flex Request Query ID" parameter in gateway settings:

![Specify the ID of the created template in the gateway settings](images/ib_gateway_flex_report3.png)

<a id="limitations"></a>
## Interactive Brokers API request limit (#limitations)

Interactive limits request sending frequency to 50 requests per second. Depending on the IB Gateway version used by the gateway, the exceeding the limit may have different consequences:

  * IB Gateway version below 974 — if the limit is exceeded, connection with IB Gateway (or TWS) is automatically closed.
  * IB Gateway version above 974 — if the limit is exceeded, connection is not closed, but request processing can slow down significantly.



You can set your own limit to the frequency of request sending by gateway, using the Rate Limit parameter. It is set to 40 by default, which is the recommended request frequency for the stable operation with IB Gateway version below 974.

<a id="accounts"></a>
## Configuring groups trading accounts (#accounts)

[Create groups](../../Platform-Setup/Groups.md) for trading accounts, whose operations will be forwarded via the Interactive Brokers gateway. For example, real\ib. Then add it to the "Groups" section of gateway settings:

![Add to the gateway the accounts group which will be managed via the gateway](images/ib_gateway_groups.png)

In the specified group, create accounts trade operations from which will be processed by the gateway.

The gateway trades in the one-to-one mode, i.e. each trading account on the Interactive Brokers side can correspond to only one account on the MetaTrader 5 platform side. Therefore, in the ["Account" section (#account)](../../Platform-Setup/Accounts/Editing-Account.md#account) of each account to be managed by the gateway you should specify an appropriate account code on the Interactive Brokers side. Specify your Interactive Brokers gateway configuration as the gateway ID.

![Specify appropriate Interactive Brokers accounts in each trading account setting](images/ib_gateway_accounts.png)

<a id="routing"></a>
## Configuring Trade Requests Routing (#routing)

Configure the routing to forward client requests to the Interactive Brokers gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

In the screenshots below all orders created by users in the real\ib\* groups for the symbols from the InteractiveBrokers\* section will be forwarded to the gateway for processing.

![Configuring Trade Requests Routing](images/ib_gateway_routing.png)

Once the rule has been added, set the required [priority (#execution)](../../Platform-Setup/Routing.md#execution) for it relative to other rules, by moving it to the desired position in the list.

<a id="marketdata"></a>
## Receiving Level 1 market data (#marketdata)

The gateway enables broadcasting of real-time financial symbol quotes to the platform. The data include the best Bid and Ask prices, as well as prices and volumes of performed trades (Last, Volume).

To start receiving symbol quotes, add them to the "Marketdata" or any nested subgroup. For example, you have added all symbols, which should be processed via Interactive Brokers, to the InteractiveBrokers\* subgroup. Create the "Marketdata" subgroup under this group and add to it all the symbols for which you want to receive quotes.

![To receive symbol quotes, add appropriate symbols to the "Marketdata" subgroup](images/ib_gateway_marketdata.png)

After that, the gateway will subscribe to appropriate Interactive Brokers data and will start delivering them to the platform. In the above example, the gateway will provide quotes for 5 symbols of the 14 symbols operated via Interactive Brokers. To stop receiving symbol quotes, move it away from the Marketdata subgroup.

Please note that the "Marketdata" symbol group must be accessible to the gateway. For example, if you create it under the InteractiveBrokers\* section which has earlier been added to the gateway settings, no additional actions will be required. If you create it under a different section, you should add an appropriate path to the gateway settings.

  * You can enable or disable the delivery of quotes at any time, by moving the symbols to/from the "Marketdata" subgroup. The gateway will immediately subscribe or unsubscribe from the relevant data.
  * Be default, Interactive Brokers enables the delivery of quotes for [up to 100 financial instruments simultaneously (#market-lines)](https://interactivebrokers.github.io/tws-api/market_data.html#market-lines). If quotes for more symbols are required, please contact Interactive Brokers and request an appropriate subscription.
  * Receiving quotes from Interactive Brokers is optional. You can use the gateway only for working with trading operations, while enabling data delivery via separate datafeeds, such as [IQ Feeder](../Data-Feeds/IQFeeder.md).

  
---  
  
<a id="multiple"></a>
## Using Multiple Gateways Simultaneously (#multiple)

The platform does not impose restrictions on the simultaneous use of multiple copies of Interactive Brokers gateways, neither technically nor from the point of view of license permissions. It means you can forward trading operations for execution via several Interactive Brokers accounts.

Please pay attention to the following requirements when configuring the gateways:

1\. All gateways must use different logins for connection to InteractiveBrokers. They must use different ports for establishing an API connection with the IB Gateway application:

![Use an individual login for each gateway](images/ib_gateway_multiple_login.png)

2\. Command Port parameter values must be different.

3\. Each gateway must use Flex token and Flex query ID specifically configured for its login.

![Ports and Flex parameters must be different for the gateways](images/ib_gateway_multiple_param.png)

4\. Appropriate gateway configurations must be specified in trading accounts on the MetaTrader 5 side. The specified Interactive Brokers accounts must be available to the selected gateways.

![Specify correct gateways and accounts in Interactive Brokers](images/ib_gateway_accounts_1.png)

5\. If several gateways have access to the same symbols in the MetaTrader 5 trading platform, it is recommended to disable the "Allow importing symbol settings" option for all but one of the gateways.

![Disable "Allow importing symbol settings" option for all but one of the gateways](images/ib_gateway_symbols_2.png)

<a id="proxy"></a>
## Configuring operation through a proxy server (#proxy)

In case the Internet access is provided through a proxy on the machine where the gateway is running, specify the relevant parameters:

  * Proxy Server — the proxy server address in the format of <protocol>://<address>:<port>. For example, socks4://192.168.0.1:4145. Supported protocols include http, socks4 and socks5. Gateway queries, such as flex report requests, will be sent through the specified server.
  * Proxy Login — a login for authentication in the proxy server.
  * Proxy Password — a password for authentication in the proxy server.



![You can specify parameters for connection through a proxy server](images/ib_gateway_proxy.png)

```

---

<a id='gateways-lmax-global-md'></a>
### 119. `Gateways/LMAX-Global.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / LMAX Global

[Previous](Cboe-FX.md) | [Next](FXCM-PRO.md)

<a id="metatrader-5-gateway-to-lmax-global"></a>
# MetaTrader 5 Gateway to LMAX Global (#metatrader-5-gateway-to-lmax-global)

[LMAX Global](https://www.lmax.com/global) is a large London-based multilateral trading facility (MTF) providing access to the institutional level liquidity. Being registered as MFT, LMAX applies exchange style trading model  the market depth is formed only by limit orders of major financial institutions. LMAX provides reliable execution within three milliseconds at more than 70 Forex and CFD symbols, transparent operation, anonymous trading and access to twenty market depth levels.

MetaTrader 5 Gateway to LMAX is a simple, fast and secure integration solution for brokers. The gateway provides institutional level liquidity when working in MetaTrader 5.

LMAX Global key advantages:

  * Over 70 Forex and CFD symbols
  * Metals, indices and commodities
  * Average trading operation execution time  4 ms
  * Processing up to 40 000 orders per second
  * No deviations, requotes and "last look" (canceling order at the last moment)
  * Commission discounts depending on a broker's turnover
  * LMAX Global trading systems (matching engine) are located in London (Equinix LD4 data center) and Tokyo (Equinix TY3 data center). The system can be accessed both via the Internet and via cross connect cable in the data center where LMAX\s servers are hosted.



The complete list of advantages and available trading instruments can be found on the [official website](https://www.lmax.com/exchange/trading "LMAX Global advantages").

<a id="getting-started-with-lmax-global"></a>
## Getting started with LMAX Global (#getting-started-with-lmax-global)

First, connect LMAX Global using the contact details on the official website: <https://www.lmax.com/global/contact>. After concluding an agreement, you will receive all necessary data for connecting to LMAX Global trading system.

> [Order MetaTrader 5 Gateway to LMAX Global](https://support.metaquotes.net/en/market/product/268)

<a id="how-the-gateway-works"></a>
## How the gateway works (#how-the-gateway-works)

MetaTrader 5 Gateway to LMAX Global is a separate LMAXGateway64.exe module that uses the MetaTrader 5 Gateway API for operation. The gateway works via two FIX channels: the first one is for trading, while the second one is for market data.

All orders entered in LMAX Global are transferred to the unified requests database. The system selects appropriate orders automatically executing opposite orders with matching parameters (symbol, price etc.)

![Gateway operation scheme](images/lmax_scheme.png)

<a id="market-data"></a>
### Market data (#market-data)

MetaTrader 5 Gateway to LMAX Global automatically imports all the necessary symbols and processes their properties. The administrator only needs to perform a primary [setup (#symbols)](LMAX-Global.md#symbols).

Price data is transmitted in real time. The gateway is capable of narrowing or expanding prices on the go: quotes can be converted according to the settings when passing them to the platform and then re-converted back to their original state when passing trade operations to LMAX Global. Detailed information on [prices conversion (#markup)](LMAX-Global.md#markup) is available below.

<a id="trading-operations"></a>
### Trading operations (#trading-operations)

Orders are sent to MetaTrader 5 Gateway to LMAX for processing in accordance with the set [routing rules (#routing)](LMAX-Global.md#routing). Processing of requests depends on the type of the order, as well as on the gateway configuration.

All traders' orders are sent to LMAX Global through a single broker account.

Order type | Execution  
---|---  
Market order | Delivered directly to LMAX Global as a market order.  
Take Profit Buy Limit Sell Limit | Depends on [Limit Orders Coverage Mode (#parameters)](LMAX-Global.md#parameters): Limit Orders Coverage Mode=Gateway (default) Limit orders are processed on the side of LMAX Exchnage. Once a limit order has been placed by a client, an appropriate order is sent to LMAX Global. There it is placed in the aggregate Depth of Market awaiting for an opposite request with the same price to appear. Thus, clients can see their requests in the Depth of Market in the client terminal in real time. Take Profit orders are processed the same way as in Limit mode. The LMAX Global system checks the availability of the required amount of funds to cover any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the work is carried out. [Margin reservation (#margin)](LMAX-Global.md#margin) of the clients should be configured for the appropriate order types in case Limit orders are directly delivered to an external system. By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client. Limit Orders Coverage Mode=Limit Limit Orders and Take Profit orders are processed on the side of the MetaTrader 5. Once a limit order is triggered, an equivalent limit order is sent with the expiration time at the end of the current trading day (intraday). Since the price specified in the order is already present in the market, the order will be executed with that price  a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. In this case, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5. A limit order with the price equal to a Take Profit level is sent to LMAX Echange at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price  a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. The client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on MetaTrader 5 side.   
Limit mode allows you to protect against slippage, as a limit order is sent to LMAX Global system with a specified price rather than a market order for execution by the current price. Limit Orders Coverage Mode=Market Limit orders and Take Profit orders are processed on the MetaTrader 5 platform side. Once they trigger, an appropriate market order is sent to LMAX Global.  
Buy Stop Sell Stop | Depends on [Stop Orders Coverage (#parameters)](LMAX-Global.md#parameters): Stop Orders Coverage=Y Delivered directly to LMAX Global. Similarly to limit orders, margin reservation of the clients should be configured for the appropriate order types on MetaTrader 5 side in case of direct delivery of stop orders to LMAX Global. Stop Orders Coverage=N Processed on the MetaTrader 5 platform side until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to the LMAX Global system.  
Buy Stop Limit Sell Stop Limit | Depends on Stop Orders Coverage: Stop Orders Coverage=Y Delivered directly to LMAX Global. Similarly to limit orders, margin reservation of the clients should be configured for the appropriate order types on MetaTrader 5 side in case of direct delivery of stop limit orders to LMAX Global. Stop Orders Coverage=N Processed on the MetaTrader 5 side. Upon order activation, an appropriate limit order is created in MetaTrader 5, and this order is then processed in accordance with the value of the Limit Orders Coverage Mode parameter.  
Stop Loss Stop Out | Processed on the MetaTrader 5 side. Once they trigger, an appropriate market order is sent to LMAX Global.  
  
> In case connection to  server is lost, the application will try to restore it repeatedly. If pending orders were executed during the disconnection period, they will be updated in the MetaTrader 5 platform after successful reconnection.

<a id="settings"></a>
## Gateway setup (#settings)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway settings](images/lmax_common.png)

Set the following parameters on the "Common" tab:

  * ID  unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Module  specify LMAXGateway64 and accept the default settings after the module selection.
  * Trading server  LMAX Global server IP-address and the port, where trade requests are processed. This information is provided by LMAX Global as parameters DNS and Port. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.  
If connection to a trade server is not required (the gateway only receives quotes from LMAX Global), leave this field empty.
  * Trading login  login for connecting the trade flow corresponding to UserName tag (553) in FIX protocol. Provided by LMAX Global.
  * Password  password for connecting the trade flow corresponding to Password tag (554) in FIX protocol. Provided by LMAX Global.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * The details for connection to the LMAX Global server where trade requests are processed will be provided during the agreement conclusion.

  
---  
  
Now, go to the "Parameters" tab.

![Gateway parameters setup](images/lmax_param.png)

Specify the following parameters values here:

  * FIX Trade TargetCompID  standard parameter of the FIX messages heading used for trading messages recipient identification. This parameter is provided by LMAX Global as the value of TargetCompID (56).
  * FIX Trade SenderCompID  standard parameter of the FIX messages heading used for a data sender identification. This parameter is provided by LMAX Global as the value of SenderCompID (49).
  * FIX Market Data Address  IP address and port of the LMAX Global server, from which market (price) data is transmitted. This information is provided by LMAX Global as parameters DNS and Port. An encrypted SSL connection to a server is established by default. If you need to establish an unencryprted connection, additionally specify the /nossl key in the address bar. For example: 10.123.100.17:10219/nossl.  
If connection to a quoting server is not required (the gateway only passes trading operations), leave this field empty.
  * FIX Market Data Username  login for connecting the trade flow corresponding to UserName tag (553) in FIX protocol. Provided by LMAX Global.
  * FIX Market Data Password  password for connecting the trade flow corresponding to Password tag (554) in FIX protocol. Provided by LMAX Global.
  * FIX Market Data TargetCompID  standard parameter of the FIX messages heading used for market messages recipient identification. This parameter is provided by LMAX Global as the value of TargetCompID (56).
  * FIX Market Data SenderCompID  standard parameter of the FIX messages heading used for a market data sender identification. This parameter is provided by LMAX Global as the value of SenderCompID (49).
  * FIX Market Data Log Enabled  if Yes, the gateway saves FIX connection (market flow) logs. Enable the parameter only in case of the gateway operation issues. The default value is No.
  * Limit Orders Coverage Mode  the mode of processing of Limit and Take Profit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:
    * Market  limit and Take Profit orders are processed on the MetaTrader 5 platform side. If an order is activated, an appropriate market order is sent to the LMAX Global system.
    * Limit  limit and Take Profit orders are processed on the MetaTrader 5 side.  
Once a limit order is triggered, an equivalent limit order is sent to LMAX Global. The order remains valid till the end of the current trading day (intraday). Since the price specified in the order is already present in the market, the order will be executed with that price  a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. In this case, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.   
A limit order with the price equal to a Take Profit level is sent to LMAX Global at the moment a Take Profit order has been activated. Since the price specified in the order is already present in the market, the order will be executed with that price  a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. The client's position will be closed partially. Control over the Take Profit position level with the remaining volume will then be carried out on the MetaTrader 5 side.   
Limit mode allows to protect against slippage, as a limit order is sent to the LMAX Global system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to LMAX Global.
    * Gateway  limit orders are processed on the LMAX Global side. Once a limit order has been placed by a client, an appropriate order is sent to LMAX Global. Take Profit orders are processed the same way as in the Limit mode.
  * Stop Orders Coverage  mode of handling stop and stop limit orders. In case of 'Y' value, these order types will be transferred to LMAX Global directly. In case of 'N' value, the orders will be processed inside MetaTrader 5 platform until their stop price is reached. After a stop order is activated, an appropriate market order will be sent to the LMAX Global system. After a stop limit order has been activated, a limit order is created, which will be processed according to Limit Orders Coverage Mode parameter value.
  * Quotes Delay â delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample â the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample â the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample â the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



  * In no circumstances it is allowed to change operations transfer mode while in operation. Changing the mode is allowed only after all client positions are closed.
  * Margin reservation of the clients should be configured for the appropriate order types [in case Limit, Stop and/or Stop Limit orders (#margin)](LMAX-Global.md#margin) are directly transferred to an external system.

  
---  
  
The next stage is to specify the groups of the clients, whose requests will be processed via the MetaTrader 5 Gateway to LMAX, as well as symbols, by which the gateway processes trading operations and broadcasts quotes.

![Configuring groups and symbols](images/lmax_groups_symbols.png)

The gateway supports [more than 100 LMAX instruments (#supported-symbols)](LMAX-Global.md#supported-symbols). Make sure to enable "Allow importing symbol settings" option. The gateway imports symbols from LMAX Global to Symbols/Preliminary/LMAX directory of the MetaTrader 5 and manages their parameters.

  * Initially, all imported symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After the symbols are relocated and trading abilities are enabled, the main trading server must be restarted.


  * Only [Market or Exchange execution](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md) can be used for the symbols. In all other cases, operations will be rejected.


  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case the symbol is not transferred and its trading ability is not turned off.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="margin"></a>
## Margin setup (#margin)

Margin reservation of the clients should be configured for the appropriate order types in case Limit, Stop and/or Stop Limit orders are directly transferred to an external system.

The external system checks the funds that are necessary to provide any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the work is carried out.

By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client.

After an order has been transferred to the external system, MetaTrader 5 platform is not able to check the client's margin sufficiency any more. After the order has been executed in the external system, the gateway cannot ignore that fact. Therefore, the appropriate trading operation is performed in the platform.

Set non-zero coefficients for the orders directly transferred to the external trading system in symbol settings for the appropriate symbols:

![Margin setup](images/integral_margin_allorders_2.png)

<a id="routing"></a>
## Configuring trade requests routing (#routing)

Configure the routing to let the client requests to be transmitted to the LMAX Global gateway. To do this, add a routing rule to the relevant [MetaTrader 5 Administrator](../../Platform-Setup/Routing.md) section.

Select "Process to dealers" as an action in common settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

The screenshots below all orders created by users in the real\lmax\* groups by symbols from the LMAX\* section will be sent to the gateway for processing.

![Configuring trade requests routing](images/lmax_routing.png)

After the correct execution of the steps described above, the gateway will be ready for work.

<a id="markup"></a>
## Changing Symbols Names and Markups (#markup)

The gateway receives the prices from LMAX Global and transmits them to clients considering markups. Thus, a brokerage company receives its profit share from each deal performed at LMAX Global. Markup values are set separately for Bid and Ask prices by each symbol:

![Changing symbol names and price correction](images/lmax_translation.png)

Besides, you can configure matching of symbol names used in LMAX Global with the names used in your MetaTrader 5 platform. For example, if the symbol name in LMAX Global is EURGBPLMAX, and it is called EURGBP in the MetaTrader 5, enter EURGBP in the "Symbol" field and EURGBPLMAX in the "Source" field.

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. Below is a schematic example of the correction:

LMAX Global | >>> | ask price | EURGBP 0.83004 | >>> | MetaTrader 5 server  
---|---|---|---|---|---  
MetaTrader 5 server | >>> | ask price | EURGBP 0.83006 | >>> | Client terminal  
Client terminal | >>> | buy limit | EURGBP 0.83006 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit | EURGBP 0.83004 | >>> | LMAX Global  
LMAX Global | >>> | buy limit execution | EURGBP 0.83004 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit execution | EURGBP 0.83006 | >>> | Client terminal  
  
A broker gains 2 pips of profit in this example. The price is sent to the client terminal only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices submitted by LMAX Global.

<a id="prices-round-off"></a>
## Prices Round Off (#prices-round-off)

During the gateway's operation, accuracy of quotes (decimal places) passed for some symbol may change in the external trading system. Decrease in price accuracy at the external trading system's side does not affect the gateway's operation. It still transmits prices with less accuracy. However, if the number of decimal places at the external system's side increases, the gateway starts rounding off the passed prices.

Suppose that the accuracy of quotes has changed from 4 to 5 digits. Obtained five-digit quotes are rounded up by the gateway and used for creating the Market Depth. The round off is always performed in broker's favor. Thus, buy requests of 1.23447, 1.23441 are rounded up to 1.2345, while sell ones of 1.23447, 1.23441 are rounded down to 1.23440.

Changes in symbol price accuracy are recorded in the gateway journal.

<a id="volume-conversion-for-different-contract-sizes"></a>
## Volume conversion for different contract sizes (#volume-conversion-for-different-contract-sizes)

The gateway automatically converts the volume of orders sent to the exchange if the symbol's contract size in MetaTrader 5 differs from its contract size on the LMAX side. For example, if the contract size on the platform side is 10,000 while LMAX provides the size of 100,000, the 1-lot order will be sent to the exchange as a 0.1-lot order.

Before changing the contract size on the platform side, make sure that you do not have open positions or orders for LMAX symbols. Restart the gateway after changing the contract size. After that an entry about mismatching contract sizes will be printed to the gateway journal, such as:

Gateway symbol AUDCHFLMAX contract sizes are different at MT5 (500000.00) and LMAX (10000.00)  
---  
  
<a id="fill-policy-and-order-expiration"></a>
## Fill Policy and Order Expiration (#fill-policy-and-order-expiration)

When sending an order from the MetaTrader 5 client terminal, traders can set the order [execution policy (#fill-policy)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#fill-policy) (FOK, IOC or Return) and [expiration time (#expiration)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#expiration) (Good Till Canceled or Today, expiration by a certain date or time is not supported). In LMAX Global trading system, these parameters are combined into one  Time in Force. Therefore, the gateway performs the following changes when passing the orders:

  * If FOK or IOC fill policy is set for an order, the same policy is applied in LMAX Global system.
  * If a market order with Return fill policy is placed, it will be passed to LMAX Global system in Good Till Canceled (GTC) mode.
  * If a limit order with Return fill policy is placed, expiration time from MetaTrader 5 (Good Till Canceled or Today) is inserted into the appropriate order parameter in LMAX Global system.
  * If a limit order is activated in MetaTrader 5 platform and the gateway works in the mode of passing limit orders (Limit Orders Coverage Mode = Limit), a limit order with Today execution policy is passed to LMAX Global system.
  * If a position take profit is activated in MetaTrader 5 platform and the gateway works in the mode of passing limit orders (Limit Orders Coverage Mode = Limit or Limit Orders Coverage Mode = Gateway), a limit order with Today execution policy is passed to LMAX Global system.



<a id="additional"></a>
## Additional (#additional)

For the proper operation of the gateway, the time on the computer where the gateway is running, should be synchronized with the master time source server. If time is not configured, the gateway will print the following error into the journal:

2016.09.30 13:34:34.576 Gateway session logout (SendingTime accuracy problem.)  
---  
  
If your computer is not a member of a domain, you can synchronize your computer clock with an Internet time server in Control Panel - Date and Time - Internet Time. Otherwise you can start time synchronization using the command line:

net time /domain  
---  
  
<a id="supported-symbols"></a>
## Supported Assets (#supported-symbols)

Currently, the gateway supports the following trading symbols:

Imported symbol name | Symbol name on the LMAX side  
---|---  
AUDCADLMAX | AUD/CAD  
AUDCHFLMAX | AUD/CHF  
AUDJPYLMAX | AUD/JPY  
AUDNZDLMAX | AUD/NZD  
AUDUSDLMAX | AUD/USD  
CADCHFLMAX | CAD/CHF  
CADJPYLMAX | CAD/JPY  
CHFJPYLMAX | CHF/JPY  
EURAUDLMAX | EUR/AUD  
EURCADLMAX | EUR/CAD  
EURCHFLMAX | EUR/CHF  
EURCZKLMAX | EUR/CZK  
EURDKKLMAX | EUR/DKK  
EURGBPLMAX | EUR/GBP  
EURHKDLMAX | EUR/HKD  
EURHUFLMAX | EUR/HUF  
EURJPYLMAX | EUR/JPY  
EURMXNLMAX | EUR/MXN  
EURNOKLMAX | EUR/NOK  
EURNZDLMAX | EUR/NZD  
EURPLNLMAX | EUR/PLN  
EURRUBLMAX | EUR/RUB  
EURSEKLMAX | EUR/SEK  
EURSGDLMAX | EUR/SGD  
EURTRYLMAX | EUR/TRY  
EURUSDLMAX | EUR/USD  
EURZARLMAX | EUR/ZAR  
GBPAUDLMAX | GBP/AUD  
GBPCADLMAX | GBP/CAD  
GBPCHFLMAX | GBP/CHF  
GBPCZKLMAX | GBP/CZK  
GBPDKKLMAX | GBP/DKK  
GBPHKDLMAX | GBP/HKD  
GBPHUFLMAX | GBP/HUF  
GBPJPYLMAX | GBP/JPY  
GBPMXNLMAX | GBP/MXN  
GBPNOKLMAX | GBP/NOK  
GBPNZDLMAX | GBP/NZD  
GBPPLNLMAX | GBP/PLN  
GBPSEKLMAX | GBP/SEK  
GBPSGDLMAX | GBP/SGD  
GBPTRYLMAX | GBP/TRY  
GBPUSDLMAX | GBP/USD  
GBPZARLMAX | GBP/ZAR  
NOKSEKLMAX | NOK/SEK  
NZDCADLMAX | NZD/CAD  
NZDCHFLMAX | NZD/CHF  
NZDJPYLMAX | NZD/JPY  
NZDSGDLMAX | NZD/SGD  
NZDUSDLMAX | NZD/USD  
USDCADLMAX | USD/CAD  
USDCHFLMAX | USD/CHF  
USDCNHLMAX | USD/CNH  
USDCZKLMAX | USD/CZK  
USDDKKLMAX | USD/DKK  
USDHKDLMAX | USD/HKD  
USDHUFLMAX | USD/HUF  
USDILSLMAX | USD/ILS  
USDJPYLMAX | USD/JPY  
USDMXNLMAX | USD/MXN  
USDNOKLMAX | USD/NOK  
USDPLNLMAX | USD/PLN  
USDRUBLMAX | USD/RUB  
USDSEKLMAX | USD/SEK  
USDSGDLMAX | USD/SGD  
USDTRYLMAX | USD/TRY  
USDZARLMAX | USD/ZAR  
XAUUSDLMAX | Gold (Spot)  
XAUUSDmLMAX | Gold (Spot Mini)  
XAUEURLMAX | XAU/EUR  
XAUAUDLMAX | XAU/AUD  
XAGUSDLMAX | Silver (Spot)  
XAGUSDmLMAX | Silver (Spot Mini)  
XAGAUDLMAX | XAG/AUD  
XPTUSDLMAX | XPT/USD  
XPDUSDLMAX | XPD/USD  
XBRUSDLMAX | UK Brent (Spot)  
XBOUSDLMAX | UK Brent (Spot) +100  
XTIUSDLMAX | US Crude (Spot)  
XTUUSDLMAX | US Crude (Spot) +100  
XNGUSDLMAX | US Natural Gas (Spot)  
AUS200LMAX | Australia 200  
STOXX50ELMAX | Europe 50  
FCHILMAX | France 40  
GDAXILMAX | Germany 30  
GDAXImLMAX | Germany 30 (Mini)  
HSILMAX | Hong Kong 50  
J225LMAX | Japan 225  
SPN35LMAX | Spain 35  
UK100LMAX | UK 100  
SPXLMAX | US SPX 500  
SPXmLMAX | US SPX 500 (Mini)  
NDXLMAX | US Tech 100  
NDXmLMAX | US Tech 100 (Mini)  
WS30LMAX | Wall Street 30  
WS30mLMAX | Wall Street 30 (Mini)  
XBTUSDLMAX | XBT/USD  
XETUSDLMAX | XET/USD  
XBNUSDLMAX | XBN/USD  
XLCUSDLMAX | XLC/USD  
XRPUSDLMAX | XRP/USD  
XBNJPYLMAX | XBN/JPY  
XBTJPYLMAX | XBT/JPY  
XETJPYLMAX | XET/JPY  
XLCJPYLMAX | XLC/JPY  
XRPJPYLMAX | XRP/JPY

```

---

<a id='gateways-moex-derivatives-md'></a>
### 119. `Gateways/MOEX-Derivatives.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / MOEX Derivatives

[Previous](MOEX-Securities.md) | [Next](DGCX.md)

<a id="metatrader-5-gateway-to-moex-derivatives"></a>
# MetaTrader 5 Gateway to MOEX Derivatives (#metatrader-5-gateway-to-moex-derivatives)

MetaTrader 5 Gateway to MOEX Derivatives allows trading futures and options on the derivatives market of the Moscow Exchange.

[The futures and options market](https://moex.com/s96) of OJSC "Moscow Exchange MICEX-RTS" is a leading trading venue for derivatives in Russia and Eastern Europe. The market combines the advanced infrastructure, reliability and guarantees of OJSC "Moscow Exchange MICEX-RTS" as well as state-of-the-art technologies for futures and options trading with more than ten years of the stable and successful market development.

The essential part of any transaction in derivatives is the settlement of a contract on a certain day in the future under fixed conditions. [The market participants](https://moex.com/ru/members.aspx?tid=35) are reliable large cap investment companies and banks.

The derivatives market offers more than 150 different futures contracts. Their full list can be viewed on the [Moscow Exchange's official website](https://moex.com/ru/derivatives/contracts.aspx).

To start your activity on the market, you should [connect to it](https://moex.com/s38), as described on the exchange's website. Brokerage and clearing companies can work on the market.

<a id="metatrader-5-gateway-to-moex-derivatives"></a>
## MetaTrader 5 Gateway to MOEX Derivatives (#metatrader-5-gateway-to-moex-derivatives)

MetaTrader 5 Gateway to MOEX Derivatives is a separate MOEXDerivativesGateway64.exe file that uses Gateway API for its operation. Gateway module is originally included in the platform delivery set. After purchasing the gateway, the trading platform license will automatically update via LiveUpdate system. This allows you to start using MetaTrader 5 Gateway to MOEX Derivatives without any limitations.

> [Order MetaTrader 5 Gateway to MOEX Derivatives](https://support.metaquotes.net/en/market/product/271)

<a id="how-the-gateway-works"></a>
## How the gateway works (#how-the-gateway-works)

MetaTrader 5 Gateway to MOEX Derivatives uses Plaza 2 protocol, which is the official software package for providing access to the exchange. Plaza 2 package has two main components:

  * P2MQRouter module is a module providing connection to exchange servers, receiving and sending messages, data encryption and decryption, as well as participant's authentication in the exchange's network. In fact, this module is an intermediate component between the exchange and a third-party software connected to it.
  * [CGate](ftp://ftp.moex.com/pub/FORTS/test/CGate/cgate_ru.pdf) library is an official program interface provided to third-party companies to create a software.



Both components are already included in MetaTrader 5 Gateway to MOEX Derivatives. Thus, no third-party software (P2MQRouter module) is required to use it. When the gateway is enabled in the terminal, P2MQRouter with necessary settings is launched on a local server. It provides a comprehensive interface for connecting MetaTrader 5 Gateway to MOEX Derivatives to the exchange.

By default, the gateway receives aggregated Market Depth from Plaza 2 streams: from FORTS_FUTAGGR*_REPL with a frequency of 10 ms or from FORTS_FUTAGGR*_FASTREPL with a frequency of 3 ms. Use the High Frequency Replication parameter to switch between them.

The gateway can optionally build the Market Depth using the journal of anonymous orders broadcast by Moscow Exchange through the FAST Multicast service in the ORDERS-LOG data channel. Unlike other data channels of the Exchange derivatives section, here the order book is broadcast in real time, which enables creation and display of the most up-to-date Market Depth. The enable this mode, fill in each of the four MarketFeed* parameters.

  * No third-party software is required to provide MetaTrader 5 Gateway to MOEX Derivatives operation.


  * Please contact the exchange to connect FAST Multicast services of the derivatives market to your servers in the collocation zone.

  
---  
  
<a id="common"></a>
## Configuring the gateway (#common)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Configuring MetaTrader 5 Gateway to MOEX Derivatives](images/moex_der_common.png)

The following parameters on the "Common" tab should be set:

  * Module — MOEXDerivativesGateway. After that the gateway default parameters installation must be allowed in the dialog request.
  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Trading server — address for connection to the exchange (not to P2MQRouter module) should be specified here in "address:port" format. In the above example, it is "test-forts.micex.com:3001" address for developers.
  * Trading login — user ID for connection to the exchange.
  * Password — password for connection to the exchange.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * Connection data (address, login and password) are provided by the exchange during the agreement conclusion.

  
---  
  
Set additional configuration parameters on the Parameters tab:

![MetaTrader 5 Gateway to MOEX Derivatives parameters](images/moex_der_param.png)

The following additional parameters are available for the gateway:

  * Trading Calendar Holidays — the exchange may have working and non-working days that are different from the MetaTrader 5 parameters for working days and holidays. This parameter redefines working/non-working days for the gateway. To add a non-working day, specify a value of the form +DDMMM. The date is specified as two digits, the month is specified as the first three letters of the month name in English. For example, +01JAN. To add a working day, specify a value of the form -DDMMM, for example, -07FEB. You can specify multiple working/non-working days, separated by semicolons, for example, + 01JAN;-07FEB.
  * Market Depth — depth of the transmitted depth of market. Depth of 5 and 20 requests are supported. The depth of 5 is used unless otherwise specified.
  * Router Listen Port — port on a local PC (127.0.0.1), where P2MQRouter module is launched by the gateway. This is the port where P2MQRouter module will accept connections from the gateway.
  * Router Direct Link1/2/3 — additional IP addresses for connection to the exchange. They are used to receive data from different streams in parallel. All addresses are provided by the exchange. The order of specifying additional addresses does not matter. For test area, use addresses test-forts.micex.com:3000, test-forts.micex.com:3003 and test-forts.micex.com:3004.
  * Broker Code — unique alphanumeric identifier of your company as the market participant. The identifier consists of three parts XXYYZZZ, where XX is a clearing company code, YY — brokerage company code, ZZZ — client code. When representing a clearing company, broker's code is specified as 00, while client's code is removed (for example, Q100, where Q1 is a clearing company code). When representing a brokerage company, client's code is specified as 000 (for example, Q1DU000, where Q1 is a clearing company code, while DU is a brokerage company one). Broker Code is provided by the exchange and used to assign numbers to client accounts.
  * Time To Start — by default, the gateway starts connecting to the exchange's server 15 minutes before the start of the main trading session (9:45 GMT+3). Some brokers may need to change this parameter. To do this, use Time To Start parameter to specify in how many minutes before the session the gateway should start connection. For example, if connection is to start at 9:35, the parameter's value should be 25.
  * Time To Sync Limits — the gateway receives fund limits by clients from the exchange and synchronizes the client balances in MetaTrader 5 appropriately before the start of a trading session. By default, the limits start arriving 5 minutes before the start of the main trading session (9:55 GMT+3). Some brokers may need to change this parameter. To do this, use Time To Sync Limits parameter to specify in how many minutes before the session the gateway should start receiving the limits. For example, in order to receive the limits at 9:50, the parameter's value should be 10. If the exchange allocates an additional morning session on a certain day, the gateway will automatically determine such a session and will synchronize data 5 minutes (or the number of minutes specified in "Time To Sync Limits" if you use a custom value) before the session start.
  * Environment — the gateway uses Plaza 2 protocol, which is the official software system providing access to the exchange. The exchange has three areas - test, learning (for practice) and real (for trading) ones. Different versions of Plaza 2 protocols are applied at each of the areas. If you connect to the learning area, set Game value for this parameter to allow the gateway to use the appropriate version of the protocol. Select Real to connect to real trading area. Set Test to connect to test area.
  * FTP Statistic Process — after the end of a trading session, the gateway downloads the official report of the exchange concerning all performed deals from the special FTP server. This report is used for control and correction of historical data in MetaTrader 5. If you want to disable the monitoring of historical data by reports, set this parameter to No.
  * Spreads Allow — inter-month spreads (security deposit benefits) are applied to some futures contracts on the derivatives market. For example, when purchasing the closest quarterly futures and the futures for the next quarter, the funds limit is decreased by the maximum value of the security deposit for both contracts. The full list of futures can be found in the ["Futures inter-month spreads" table on the exchange's website (#futures)](https://moex.com/s206#futures). The gateway automatically imports the necessary spread settings if Yes is specified in Spreads Allow parameter.
  * Symbols Path — path for importing the exchange symbols. By default, if this parameter is absent, the gateway imports the exchange's trading symbols to \Preliminary subdirectory with trading ability disabled. A system administrator should manually relocate imported symbols to the proper group and allow trading for them. If this parameter is present, the gateway imports trading symbols following the specified path. The ability to trade the symbols is enabled immediately. Thus, the administrator has no need to additionally configure the symbols. For example, if MOEX is specified in the parameter, then futures contracts are automatically added to MOEX\FORTS\*, Standard section contracts are added to MOEX\Standard\*, while expired contracts are automatically transferred to MOEX\FORTS\Expired\*.
  * Symbols Path Expired — path for transferring the expired symbols. By default, if this parameter is not specified, all expired contracts are moved to \Expired subdirectory of the folder specified in Symbols Path parameter. In the above example, it is MOEX\FORTS\Expired\*. This parameter allows re-configuring the path for transferring the expired contracts.
  * Options Allow — in addition to futures, the derivatives market allows trading options as well. If Yes, the gateway automatically imports available options to \FORTS\Options subdirectory of the directory set in the Symbols Path parameter. The gateway also handles trade requests for these symbols.
  * TP Coverage As Limit Order — the policy of passing the activation of a take profit level to the exchange. If set to Yes, an opposite limit order corresponding to the take profit activation level is passed to the exchange. If set to No, an opposite limit order at the minimum or maximum price (depending on the order direction) is passed to the exchange when a take profit is activated. For buy orders, current session's [highest price (#prices)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#prices) is used; for Sell orders the lowest price is used. For example, when the Take Profit of a long position triggers, a limit sell order at the symbol's lowest price as of the current moment is sent.
  * Limits Sync Full — if Yes, clients' positions on the exchange are automatically imported to MetaTrader 5 in the morning, before the main trading session. Positions in MetaTrader 5, which differ from exchange positions, will be modified to conform to exchange positions (in case of a divergence, existing positions are completely closed and new ones are opened). This option has been added to automatically fix emergency possible out of sync state.
  * High Frequency Replication — Moscow Exchange provides the ability to receive market data with [high frequency](https://moex.com/n4171) — once per 3 ms instead of once per 10 ms. In order to use this ability, enable the appropriate additional service at the exchange and set the High Frequency Replication parameter to Yes. Also, replace the trade server address with the one, from which the high-frequency data is to be received. The address is provided by the exchange when enabling the service.
  * Limits Sync Exclude — allows disabling synchronization of positions and balances for the specified client groups. The platform allows transmitting trading operations from one account through different gateways. To do this, multiple accounts in external systems corresponding to different gateways are registered in the account. There are three gateways for the Moscow Exchange. Each of them synchronizes the trading state and limits. The possibility to disable synchronization allows to prevent overwriting of data about positions and limits during simultaneous operation through these gateways. Specify the list of groups for which the gateway should not synchronize positions and balances in this parameter. Groups can be specified using the "*" mask.
  * Trade Limit allows setting the overall limitation on the number of trades sent per second for the gateway. If 0 (default), no check is performed. The maximum possible value is 16384. In case of a greater value, no check is performed.
  * Trade Limit Default allows setting the limitation on the number of trades sent by separate clients. For example, if 50 is specified, then each client can send no more than 50 trades per second via the gateway (unless the client limit is overridden by the Trade Limit <account> type parameter). If 0 (default), no check is performed.
  * Trade Limit <account> parameters allow setting the limitation on the number of trades per second sent by certain clients. You can set several parameters of that kind. For example: Trade Limit 10008628 = 7, Trade Limit 10008589 = 5. The exchange account code without a broker's code (set in the Broker Code parameter) is used in <account> — on the platform side, this code is set in the client record as an [account number in the external trading system (#trade-accounts)](../../Platform-Setup/Accounts/Editing-Account.md#trade-accounts). If 0 (default), no check is performed for the specified client. The maximum possible value is 256 trades per second. Also, no check is performed if a larger value is specified.  
Before issuing a trade request to the exchange, the gateway checks the limitation on the client account and throughout the entire gateway (brokerage account). If the check fails, the gateway does not send the client's trade and returns the MT_RET_REQUEST_TOO_MANY response code. The following entries are made in the gateway journal:



2017.11.27 18:26:21.224 Gateway account HO00001 trade transactions per second limit (5) exceeded   
2017.11.27 18:26:21.572 Gateway gateway trade transactions per second limit (7) exceeded  
---  
  
  * Password Change — this parameter determines whether the gateway should generate for the current login a new password for connecting to the exchange if the old password expires in less than 7 days. The parameter is set to No by default which means that the function is disabled. Please see Password Change for further details.
  * NewsCategory — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



This group of parameters is used for setting up the receipt of anonymous requests via the FAST Multicatst service:

  * Market Feed Config Url — channel parameters for receiving market data from the exchange are described in XML files. These files are available on the [FTP server of the exchange](https://ftp.micex.com/pub/FAST/Spectra/templates/MOEX/). Specify here the path to the file, which describes connection to the ORDERS-LOG channel (separate configuration files are available for real and testing data). Configuration file can be copied to a local server. In this case, the appropriate path should be specified in this field.
  * Market Feed FAST Templates Url — data transmitted via FAST protocol are unpacked using the special template. Specify here the path to the template file, it is available on the [Exchange's FTP server](https://ftp.micex.com/pub/FAST/Spectra/templates/MOEX/). You can specify the FTP path or copy the file to a local server and specify the appropriate local path to it.



> Market channel parameters and template files downloaded via FTP are saved in the directory [gateway folder]\downloads. If the gateway fails to download updated files, it will use earlier downloaded files stored in this folder. The following rules apply here:

  * Market Feed A Bind — the address of the local interface the connection will be bound to, to receive market data through channel A (all data from the Exchange are duplicated on two channels).
  * Market Feed B Bind — the address of the local interface the connection will be bound to, to receive market data through channel B (all data from the Exchange are duplicated on two channels).



If at least one of the above parameters is not filled, the gateway will receive Market Depth data from Plaza 2 streams.

Also, the gateway automatically switches to receiving of Market Depth data from Plaza 2 in the following situations:

  * If it is unable to subscribe to FAST Multicast newsletter
  * In case of issues while reading the incoming data stream
  * If the status of order journal of an instrument cannot be restored after an error, for more than 5 minutes



Appropriate messages are written to the gateway log in this case:

2019.02.07 09:58:12.350 Gateway failed to initialize FAST Market Data service, service will not work  
  
2019.02.07 09:58:48.856 Gateway FAST Market Data service stopped, market depth changes will be received from Plaza2  
  
2019.02.07 09:58:59.657 Gateway can not recover FAST market data state more than 300 seconds, number: 64512, feed: ORDERS-LOG, instrument: 582383  
2019.02.07 09:58:59.657 Gateway failed to apply FAST Market Data transaction, market depth will be received from Plaza2  
---  
  
> Please contact the exchange to connect FAST Multicast services of the derivatives market to your servers in the collocation zone.

On the Groups tab, specify the mask for the groups of clients who will trade in the derivatives market. The gateway will only receive trade requests from the clients included in the allowed groups list.

![Configuring groups for MetaTrader 5 Gateway to MOEX Derivatives](images/moex_der_groups.png)

If you configure importing the limits via the gateway, make sure to enable "Allow importing traders balances" option. This will allow the gateway to synchronize clients' balances in MetaTrader 5 with exchange account limits.

Limits are synchronized in the following cases:

  * launching/re-launching the gateway during a trading session;
  * five minutes before the start of the main trading session;
  * after the trading session when the clearing data is ready;
  * in case funds are withdrawn/accrued on the client's stock account.



> A group of clients trading in the derivatives market should be configured correctly.

On the Symbols tab, specify the symbols available for the gateway. The gateway will receive quotes and perform trade operations for these symbols. Also, the settings will be automatically updated for them in case import of symbols is allowed:

![Configuring symbols for MetaTrader 5 Gateway to Moex Derivatives](images/moex_der_symbols.png)

It is recommended to enable all symbols at this tab (*). Also, make sure to enable "Allow importing symbol settings" option. MetaTrader 5 Gateway to MOEX Derivatives adds necessary symbols and manages their settings on its own.

  * If the Symbols Path parameter is set, the gateway will import all new symbols to the subgroup specified in it. The trading ability is enabled immediately for all symbols. 
  * If the Symbols Path parameter is not set, the gateway will import symbols to the "\Preliminary" subgroup. In this case, the system administrator must move imported symbols to the proper subgroup and allow trading for them.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the configuration is updated. In this case the symbol is not transferred and its trading ability is not turned off.
  * In case some changes are implemented to the Depth of Market parameter of the symbol settings, the gateway and a history server must be restarted to let the changes take effect. In fact, restart is required after any change in the symbol settings.



  * On Moscow Exchange's Derivatives Market, an instrument cannot be traded during the evening session of the day on which it appeared. At an attempt to trade such an instrument, the gateway will return the "market closed" error.
  * The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

  
---  
  
<a id="config-groups"></a>
## Groups Configuration and Using Profit/Loss for the Current Trading Session (#config-groups)

According to the exchange rules, profit obtained during a trading day cannot be used before clearing is performed. In fact, only clearing determines the financial results of all transactions during the day. The profit received by a client during the current trading session is accumulated during the trading session and released only after intermediate or main clearing becoming available for use by the client for further trade.

In order to avoid a situation in which a client who suffered losses will try to continue trading, fixed loss is withdrawn immediately.

In this regard, the following parameters should be specified in "Profit/loss in free margin" block of Margin tab in the settings of the group that will operate on the derivatives market:

![Configuring a client group for trading in the derivatives market](images/moex_der_margin.png)

Stop Out value specified in this tab does not matter. Orders and positions created via the gateway are not removed/not closed on MetaTrader 5 side when Stop Out is triggered. Find more information on margin settings in the [appropriate section (#margin)](../../Platform-Setup/Groups/Group-Settings.md#margin).

All financial accounting on the derivative market is done in Russian rubles. Thus, Russian rubles (RUR) should be specified as deposit currency in the group settings:

![Configuring a client group for trading in the derivatives market](images/moex_der_group_common.png)

<a id="configuring-trade-requests-routing"></a>
## Configuring trade requests routing (#configuring-trade-requests-routing)

To direct client requests concerning derivatives market symbols to the gateway, the [routing rules](../../Platform-Setup/Routing.md) should be set. Examples can be found in the articles concerning the gateways to other trading systems, for example: [GBOT (#routing)](https://support.metaquotes.net/en/articles/332#routing), [DGCX (#routing)](https://support.metaquotes.net/en/articles/330#routing), etc.

<a id="configuring-trading-accounts"></a>
## Configuring trading accounts (#configuring-trading-accounts)

Each client on MetaTrader's side should be provided with a corresponding separate trading account on the exchange. After an account is opened at the exchange, it should be connected with the account within the platform. Open the appropriate client account and move to Account tab:

![Configuring the account](images/moex_der_account.png)

A new entry should be added in "Trade accounts" section. Select MetaTrader 5 Gateway to MOEX Derivatives in "Gateway ID" field. Specify the client code in "Account" field. The prefix corresponding to Broker Code parameter in the gateway settings is removed from the client code. During the gateway operation, the final client's code is generated using Broker Code and the client code. For example, if Broker Code is Q1DU, while client code is 001, then the client account at the exchange is Q1DU001. Similarly, if Broker Code is Q1 and the client code is ST005, then the client account at the exchange is Q1ST005.

<a id="risk-management-system"></a>
### Risk management system (#risk-management-system)

Considering trading status of each client account allows the exchange to perform client-by-client risk management. Such control is an addition to the conventional risk management system of MetaTrader 5 platform. Thus, the ability of an end customer to perform each trading operation is controlled both on MetaTrader 5 and exchange's levels.

The gateway imports trading symbols with the appropriate settings, so that the collateral calculation algorithm for orders and positions fully corresponds to the exchange calculation algorithm.

MetaTrader 5 risk management system provides control of client positions and their collateral in real time both on client terminal's and trade server's sides. Besides, the platform allows [accounting total positions](https://support.metaquotes.net/en/docs/mt5/manager/interface/toolbox/toolbox_summary) of all clients of a brokerage company via MetaTrader 5 Manager terminal. The system controls occurrence of [Margin Call and Stop Out](https://support.metaquotes.net/en/docs/mt5/manager/margin_calls) status for each client sending appropriate notifications both to a client and brokerage company managers if necessary.

<a id="processing-of-market-orders"></a>
### Processing of Market orders (#processing-of-market-orders)

Since placing of market orders on the Moscow Exchange derivatives market is not supported, the gateway forwards market orders as limit orders with the minimum or maximum price depending on the order direction. The current session [highest price (#prices)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#prices) is used for Buy orders, while the lowest price is used for Sell orders.

<a id="synchronizing-trading-status"></a>
### Synchronizing trading status (#synchronizing-trading-status)

If a client's exchange account already has a fund limit and/or open positions at the time of the gateway launch, the account status should be synchronized with MetaTrader 5. To do this, highlight the line of the gateway and the corresponding number of the account at the exchange in "Trade accounts" section. Then click Synchronize and Synchronize All.

After that, the balance and the client's open positions will be brought in line with the exchange. Synchronization of pending orders is not supported. Below is an example of a trading account in MetaTrader 5 client terminal after synchronization:

![Client's trading status in MetaTrader 5 terminal](images/moex_der_sync.png)

This example shows that two open positions have appeared at the account after the synchronization. Client's account at the exchange is shown in Comment column. The balance and account limit at the exchange have also been synchronized. The lower line of Trade tab displays the current status of the client's account:

  * Balance — client limit, not accounting for the results of currently open positions;
  * Equity — money on the client account regarding financial results of currently open positions;
  * Margin — amount of funds reserved on the client's account as a collateral;
  * Free Margin — amount of free funds that can be used for trading. This parameter is calculated as Equity - Margin;
  * Margin Level — percentage of the account equity to the margin volume (Equity / Margin * 100).



As a result of the account synchronization with the exchange, deals marked by special comments appear in the client's history:

![Client's trading history](images/moex_der_history.png)

In the example above, the client's exchange account had a limit equal to 100 000 RUR, as well as two positions. After synchronization, four entries have appeared in the history:

  * The "balance" type deal used for synchronizing the client's balance and account limit at the exchange. The deal marked as "Synchronization".
  * The "correction" type deal used for synchronizing the client's balance and account limit at the exchange. The deal marked as "Synchronization".
  * The deal for buying si-6.13 symbol marked as "opened due synchronization".
  * The deal for selling rts-6.13 symbol marked as "opened due synchronization".



<a id="charging-variation-margin"></a>
### Charging variation margin (#charging-variation-margin)

The variation margin is charged based on the results of intermediate and main clearing. The next example shows the deals in the client history that are created as a result of charging the variation margin.

![Position re-opening deals with charged variation margin](images/moex_der_variation.png)

Two pairs of deals are displayed in the example:

  * closing positions at a settlement price for si-6.13 and rts-6.13 symbols with [variation margin close] comment;
  * re-opening positions at a settlement price for si-6.13 and rts-6.13 symbols with [variation margin open] comment.



<a id="profit-for-the-current-session"></a>
### Profit for the Current Session (#profit-for-the-current-session)

The profit received by a client during the current trading session is unavailable for re-investing. It is accumulated during the trading session and released only after intermediate or main clearing becoming available for use by the client for further trade.

Below is an example of closing a profitable trading position during the trading session.

![Open trading position](images/moex_der_profit.png)

Profit received after closing the position will be shown in the balance but it will not be available for use till the intermediate or main clearing. The total accumulated profit is displayed in "Blocked" field of the trading status line:

![Total accumulated profit](images/moex_der_blocked.png)

"Blocked" field value is reset to zero after the clearing.

<a id="depositingwithdrawing-funds-from-the-account"></a>
### Depositing/Withdrawing Funds from the Account (#depositingwithdrawing-funds-from-the-account)

When depositing or withdrawing the funds from the account, the limit at the exchange is synchronized with the client's balance on MetaTrader 5 side. The appropriate balance operations with comments like "FORTS, account XXX", where XXX is the number of the client's account, appear in the client's deals history.

Updating the account limit in MetaTrader 5 does not lead to the account limit update at the exchange, as such a mechanism is currently not provided.

<a id="charging-commissions"></a>
## Charging commissions (#charging-commissions)

The exchange charges commission for each performed deal. Commission value is received by the gateway and added to the description of each deal performed at the exchange in Commission field.

Brokerage companies can take account of their own commissions in any way. In actual practice, commission is usually considered at the broker's back-office level and affects the client limits before the start of the trading session. However, it is impossible to identify this commission in the history of client deals, because there is no clear indication that this is exactly a broker's commission in balance operations performed during the synchronization of limits.

Besides, broker's commission can be additionally taken into account by means of MetaTrader 5. More details are available in the ["Commission settings"](../../Platform-Setup/Groups/Commission-Settings.md) section. In this case, commission will also be considered at the back-office level and affect client limits before the start of the trading session but the amount of the commission will be shown in real time in the client terminals.

Accounting of commissions in MetaTrader 5 should strictly comply with accounting at the broker's back-office level.

<a id="delivery-of-futures-contracts"></a>
## Delivery of futures contracts (#delivery-of-futures-contracts)

All futures contracts delivery deals are displayed in clients' history as special technical deals performed by the exchange.

  * Settlement contracts — positions are closed at a settlement price and the appropriate profit/loss is deposited/withdrawn.
  * Equity futures — upon delivery, technical deals of positions closing are performed. An appropriate position is opened for a client on the market.



<a id="history-data-synchronization"></a>
## History Data Synchronization (#history-data-synchronization)

During the conventional gateway operation, time and prices used to generate bars strictly correspond to the exchange data. All charts are generated using the prices and time of actual deals executed at the exchange.

After the end of a trading session, the exchange publishes the official report on the performed deals. This report is used by the gateway for data management. In case of any discrepancies, historical data is corrected in accordance with the report.

If the gateway is temporarily stopped and then relaunched again during the trading session, missing fragments of historical data are automatically restored (synchronized).

During the initial installation in MetaTrader 5, the gateway automatically imports historical data for all symbols for the last year since the launch of the gateway.

<a id="password-change"></a>
## Password change (#password-change)

In accordance with the Exchange policy, the account password for connection to MOEX must be changed every 90 days. Logging in with an expired password is impossible.

To avoid an unexpected interruption of your gateway due to an expired password, it can use a special mechanism for automatic password change. The mechanism is controlled via the "Password Change" parameter.

If the "Password Change" parameter is disabled (the value is "No"), then 30 days before the expiration of the current password the gateway starts displaying an appropriate message, prompting to change the password. This message will appear in the log every day, before the trading start time:

Gateway password for current exchange login 'TradingLogin' will expire in 15 days at 2020.12.30 12:00, please change current password manually or enable gateway parameter 'Password Change'  
---  
  
If the parameter is enabled (the value is "Yes"), then 30 days before the password expires, the gateway starts displaying a warning every day before the start of trading, notifying that the password will be changed automatically 7 days before its expiration:

Gateway password for current exchange login 'TradingLogin' will expire in 14 days at 2020.12.29 12:00, password will be changed automatically 7 days before expiration  
---  
  
7 days before password expiration, the gateway sends a password change request to the exchange. The new password is generated randomly. It will be displayed twice in the gateway log: before sending a request to the exchange and after receiving a password change confirmation:

Gateway password for current exchange login 'TradingLogin' will expire in 6 days at 2020.12.21 12:00, password will be changed   
Gateway change password request sent, new password: NE@1fFtt   
Gateway current password for login 'TradingLogin" on spectra-t1.moex.com:3001 changed, new password: NE@1fFtt  
---  
  
After the password is changed, the gateway will start using the new password value for further connections, and this no additional action is required.

  * The new password is saved to the settings.dat file in the gateway working directory. If this file is deleted, enter the new password manually in gateway settings. It can be found in the gateway log as described above.
  * When the password is changed using third-party software or upon request to the exchange, specify a new password in gateway settings. This is enough for further gateway operation.

  
---  
  
<a id="gateway-operation-management"></a>
## Gateway Operation Management (#gateway-operation-management)

To receive data on the gateway operation, request its logs via MetaTrader 5 Administrator. Select the gateway and move to Journal tab.

The following entries indicate that the gateway started its operation successfully:

Gateway  synchronized with FORTS server  
---  
  
The following entry indicates successful synchronization of the clients' limits:

Gateway clients limits synchronized  
---  
  
Use "session" keyword to request data on trading session completion. Session ID (4293 in the example), as well as time of its completion (2013.04.09 12:45:00) are specified in such entries.

Gateway  trade session 4293 on SEBM-4.13 finished at 2013.04.09 12:45:00  
---  
  
To receive data on the session's settlement price, request the journal using "variation margin" key phrase. In the example below, the settlement price for RTS-6.13 symbol is equal to 139750:

Gateway execution sending complete - variation margin for RTS-6.13, settlement price: 139750, account 'XO0'  
---  
  
The following special entries are made in the gateway journal to analyze operations processing speed:

Gateway  order #736398 - message process time: 31.322 ms (gateway time: 0.331 ms, exchange time: 30.991 ms)  
---  
  
The following parameters are shown here:

  * message process time - total time between sending a message to the exchange and receiving an answer;
  * gateway time - time spent by the gateway to send a message;
  * exchange time - time spent by the exchange to process a message and send an answer to the gateway.



Apart from the gateway journal, P2MQRouter module operation journal can also be analyzed in case of any issues. This module is launched by the gateway when starting its operation. Its operation journals are located at the history server in \Gateways\FORTS Gateway\\[gateway configuration name]\Plaza 2\logs directory.

<a id="operations"></a>
## Gateway Service Operations (#operations)

The gateway can perform various service operations on accounts during operation.

Deals with the type "Correction" and with the comment "[synchronization]" are formed in the following cases:

  * When you manually synchronize an account from the Administrator terminal
  * When synchronizing limits Time To Sync Limits minutes before the start of the morning session, if the Limits Sync Full parameter is enabled



Deals with the type "Correction" and with the comment "FORTS, account XXXXX" are formed in the following cases:

  * When synchronizing limits Time To Sync Limits minutes before the start of the morning session, if the Limits Sync Full parameter is enabled
  * When synchronizing limits, if the gateway is launched during the trading session or later than "Time To Sync Limits" minutes before the start of the trading session
  * When synchronizing limits after the completion of the main clearing



Deals with the type "Balance" and with the comment "FORTS, account XXXXX" are formed in case the balance on the exchange is changed during the trading session: In this case, you should contact the exchange to find out the reasons for balance changes. This is usually associated with replenishment/withdrawal of funds on the exchange account.

```

---

<a id='gateways-moex-securities-md'></a>
### 119. `Gateways/MOEX-Securities.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / MOEX Securities

[Previous](MOEXFX.md) | [Next](MOEX-Derivatives.md)

<a id="metatrader-5-gateway-to-moex-securities"></a>
# MetaTrader 5 Gateway to MOEX Securities (#metatrader-5-gateway-to-moex-securities)

MetaTrader 5 Gateway to MOEX Securities allows trading stocks and bonds on the [Moscow Exchange Equity and Bond Market](https://moex.com/s338).

It includes two markets:

  * Equity Capital Market — Russian and foreign shares, depositary receipts, fund shares, ISUs, and ETFs. The main trading mode is T+2 order book (Main Trading Mode T+). Trading is performed with a central counterparty, partial collateral and deferred execution. Settlement and delivery are performed two days after a trade is conducted (T+2).  
The gateway supports only shares.
  * Debt Capital Market — federal loan bonds (OFZs), regional and municipal bonds, Russian corporate bonds (including exchange ones) denominated in rubles and foreign currency, corporate Eurobonds and sovereign Eurobonds of the Russian Federation.  
The gateway supports only OFZs. Trading is performed with a central counterparty, partial collateral and deferred execution. The main trading mode for OFZ is T+1 order book (Main Trading Mode T+). Settlement and delivery are performed the next day after a trade is conducted (T+1).



<a id="metatrader-5-gateway-to-moex-securities"></a>
## MetaTrader 5 Gateway to MOEX Securities (#metatrader-5-gateway-to-moex-securities)

MetaTrader 5 Gateway to MOEX Securities is a separate MOEXSecuritiesGateway64.exe file that uses Gateway API for its operation. Gateway module is originally included in the platform delivery set. After purchasing the gateway, the trading platform license will automatically update via LiveUpdate system. This allows you to start using MetaTrader 5 Gateway to MOEX Securities without any limitations.

> [Order MetaTrader 5 Gateway to MOEX Securities](https://support.metaquotes.net/en/market/product/273)

<a id="general"></a>
## Common trading principles and their implementation in MetaTrader 5 (#general)

Trading in the market is regulated by the exchange rules: [Trading Rules of the Closed Joint-Stock Company "MICEX Stock Exchange".](https://fs.moex.com/files/926) Let's consider some of the key features and examples for more clarity.

In the stock market, the result of a transaction is immediately displayed on the client trading status: an open position appears, and an appropriate amount of funds is withdrawn from the balance. Depending on the instrument, the actual settlement may occur the next day or the second day after the position was opened (T+). However, unlike the FX section, positions are not moved between symbols with different calculation periods (for example, from USDRUB_TOM to USDRUB_TOD). Position on the same instrument is displayed on MetaTrader 5 side, while all operations related to moving and swapping are carried out on the exchange side. The resulting client status is then imported via the limit files.

Groups of instruments

Securities market Instruments are divided by [type and trading mode](ftp://ftp.moex.com/pub/ClientsAPI/ASTS/docs/ASTS_Markets_and_Boards.pdf):

  * TQBR — T+, Shares and debt warrants (DW);
  * TQDE — T+, [D Bonds](https://moex.com/s1858);
  * TQIF — T+, Investment units;
  * TQOB — T+, Bonds;
  * TQQI — T+, [mode for qualified investors](https://moex.com/s1434);
  * TQTF — T+, foreign exchange traded funds (ETFs);
  * AUCT — Auction;
  * SPEQ — technical transactions.



The instrument groups the gateway is to work with are defined by the Trades Mode parameter. By default, all groups are enabled, except for AUCT. SPEQ transactions are transmitted by the gateway regardless of the settings.

The same instruments can be traded in different modes. Execution results are displayed on the same position. For example, it is possible to buy shares by auction and in the order book, and this affects the unified position for the instrument.

Repo transactions

MetaTrader 5 Gateway to MOEX Securities does not allow repo deals, though it correctly imports the appropriate transactions to MetaTrader 5 from the external system. Thus, clients are able to see the current status and history of accounts in their terminals.

Repo deals are marked "repo leg 1" and "repo leg 2" in trading history for each transaction party. Target repo transactions are marked "target repo leg 1" and "target repo leg 2".

Auction

Before the start and after the end of each trading session, an auction is performed in the securities market to determine the fair instrument price. [Opening auction](https://moex.com/s1647) starts at 9:50 and ends at 10:00 (exchange time). [Closing auction](https://moex.com/s1173) is held from 18:40 to 18:50.

Transactions performed during an auction on MetaTrader 5 side are not marked in any particular way.

Bonds

The gateway supports trading OFZs only. The bonds have two key parameters:

  * Face value — initial value set by an issuer.
  * Accrued interest — accumulated coupon interest (part of the coupon interest calculated in proportion to the number of days since the coupon bond issuance or the last coupon interest payment).



Profit on MetaTrader 5 side is calculated as the difference between the prices of a position at the time of opening and closing. Position price is defined as follows:

Price/100 * Face value * Volume in lots * Contract size + Accrued interest * Volume in lots * Contract size  
---  
  
The price is divided by 100 since bond prices are passed as a face value percentage.

The current floating profit at bonds is calculated without an accrued interest:

Price/100 * Face value * Volume in lots * Contract size  
---  
  
At the end of a trading session, profit by positions can be corrected according to the exchange data.

Margin trading

Trade is marginal and contractual obligations are delayed in time. Until the time of settlement of obligations, the margin is locked on the client's account. The margin is defined by [discounts](../../Platform-Setup/Symbols/Symbol-Settings/Margin-Rates.md) relative to the current price of the instrument. Discounts are set by the broker, however they cannot be lower than the values ​​determined by [National Clearing Centre](https://www.nkcbank.com/viewCatalog.do?menuKey=36) (NCC). Due to the discounts, clients can make transactions with a leverage, i.e. open positions investing a larger sum than is available on their account.

<a id="principles"></a>
## How the gateway works (#principles)

The gateway receives market data on trading on Moscow Exchange via Multicast. This is a UDP protocol that allows packets to be transmitted to multiple recipients. Find the details of the protocol in ["Market Data Multicast Ver3.3 User Guide"](https://ftp.micex.com/pub/FAST/ASTS/docs/Archive/Rus_Market_Data_Multicast_User_Guide_Ver3.3.3.pdf). The system administrator must configure the server where the gateway is running to receive data.

The UDP protocol does not have built-in methods to ensure reliability, ordering, or data integrity, which on the one hand makes it unreliable. But on the other hand, it saves time and money required to deliver data to clients. This provides data delivery to clients with minimum delay. All transmitted data are doubled to control their integrity. The gateway receives market data from the Exchange in four tables:

  * Trades executed on the Exchange.
  * Trade statistics.
  * Depth of Market.
  * List of instruments.



To deliver each data type, four connections are created: two connections for the incremental channel where only changes relative to the previous state are transmitted, and two for the so-called snapshots (the state at a certain time).

For committing trade operations and receiving the trading status of clients, the gateway uses three FIX services, for each of which a separate connection is created:

  * MFIX Trade - entering and canceling orders and receiving order execution reports.
  * MFIX Drop Copy - receiving the stream of orders and deals from other terminals (other than MetaTrader 5).
  * MFIX Trade Capture - sending all trades of all accounts bound to the current FIX identifier of the broker.



Accordingly, three FIX IDs are required. Read more about the FIX services in ["Moscow Exchange public FIX 4.4 interface specification for Securities and FX markets"](ftp://ftp.micex.com/pub/FIX/ASTS/docs/public_fix44_interface_in_russian_v_4.pdf). If any of the services FIX is not required, it can be omitted. Simply do not specify its address in the gateway settings.

<a id="integration"></a>
## Integration with broker's back office (#integration)

The relevant trading client state in MetaTrader 5 is maintained using the client limiting interface provided by the gateway. Limiting is implemented through import of limit files in the QUIK format. The detailed format description is available in the [QUIK WorkStation reference](https://www.quik.ru/depot/quikref.zip). This format has been selected due to the fact that the platform is currently used by most of the brokers that provide access to Moscow Exchange, and therefore such an approach is the most simple and convenient one to move to MetaTrader 5.

In the gateway settings, specify the address (ftp or local address), from which the gateway shall automatically read the limit and correction files and synchronize client states in MetaTrader 5. The limit file can be used at any moment of gateway operation. Once the administrator adds a file to the specified directory, the gateway will process it and will set the client status in accordance with it. This behavior can also be used to recover client states in case of failures.

Limit correction files are used to reflect the limit changes in the broker's back-office system. The gateway processes them only in trading hours (10:00 to 23:50 Moscow time). Correction files are processed in accordance with the following algorithm:

  * When the correction file is updated, the gateway starts analyzing it.
  * It parses all the correction entries from the file one by one.
  * The gateway finds the entry with LIMIT_ID (the correction identifier is unique within a file and within one trading day) equal to LIMIT_ID_LAST (the identifier of the last processed correction).
  * All subsequent entries are processed and applied to the clients' trading states. While each subsequent entry is processed, the value of LIMIT_ID_LAST is updated to avoid repeated application of corrections.
  * As soon as processing is over, the gateway uploads the file with the correction results. The file is of the QUIK system format. The file is uploaded at the address specified in the [gateway settings (#param)](https://support.metaquotes.net/en/articles/411#param).
  * At the beginning of each trading day, the ID of the last processed correction is reset.



<a id="configuring-the-gateway"></a>
## Configuring the gateway (#configuring-the-gateway)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway connection settings](images/moex_sec_common.png)

The following parameters on the "Common" tab must be set:

  * Module — MOEXSecutitiesGateway64. After that the gateway default parameters installation must be allowed in the dialog request.
  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Trading server — address for connection to the MFIX Trade service.
  * Trading login — login (FIXTradeSenderCompID) for connection to MFIX Trade.
  * Password — password for connection to MFIX Trade.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * Connection data (address, login and password) are provided by the exchange.

  
---  
  
Additional configuration parameters must be set on the Parameters tab:

![MetaTrader 5 Gateway to MOEX Securities parameters](images/moex_sec_param.png)

The following additional parameters are available for the gateway:

  * Trading Calendar Holidays — each exchange works in accordance with its own trading calendar. By default, non-working days for the gateway are Saturday and Sunday. Using this option, you can override the working/non-working days for the gateway. To add a non-working day, specify a value of the form +DDMMM. The date is specified as two digits, the month is specified as the first three letters of the month name in English. For example, +01JAN. To add a working day on Saturday or Sunday, specify a value of the type -DDMMM, for example, -07FEB. You can specify multiple working/non-working days, separated by semicolons, for example, + 01JAN;-07FEB.
  * Market Feed ConfigUrl — parameters of channels for receiving market data from the exchange are described in the XML file. This file is available on the [Exchange's FTP server](https://ftp.micex.com/pub/FAST/ASTS/config/). Specify the path to the file, depending on what data you want to receive (real or test). Configuration file can be copied to a local server, the appropriate path should be specified in this field. The gateway reads data for connection to the following channels (set by the connection_id parameter in the file):


  *     * OBR and OBS — an incremental channel and a channel of snapshots for transmitting the depth of market.
    * TLR and TLS — an incremental channel and a channel of snapshots for transmitting trading operations.
    * MSR and MSS — an incremental channel and a channel of snapshots for transmitting trade statistics.
    * IDF — a channel for transmitting the list of financial instruments.
  * Market Feed FAST Templates Url — all market data are transmitted through the FAST protocol. Transmitted data are unpacked using the special FAST template. Specify here the path to the template file, it is available on the [Exchange's FTP server](https://ftp.micex.com/pub/FAST/ASTS/template/). You can specify the FTP path or copy the file to a local server and specify the appropriate local path to it.



> Market channel parameters and template files downloaded via FTP are saved in the directory [gateway folder]\downloads. If the gateway fails to download updated files, it will use earlier downloaded files stored in this folder. The following rules apply here:

  * Market Feed A Bind — the address of the local interface the connection will be bound to to receive market data through channel A (all data from the Exchange are duplicated on two channels).
  * Market Feed B Bind — the address of the local interface the connection will be bound to to receive market data through channel B (all data from the Exchange are duplicated on two channels).
  * Trade Account — the account used for registering the transaction performed through the gateway on the exchange.
  * FIX Trade TargetCompID — FIX messages heading standard parameter used for a message recipient identification for the MFIX Trade service. The remaining connection parameters are specified on the "Common" tab in the gateway settings.
  * Trade Commission Use — this parameter sets the use of commissions from the exchange. The commissions are specified in each transaction received from the exchange. If the parameter is set to "Yes", this value is used in the platform. If set to "No" (default), the broker can [configure commission calculation](../../Platform-Setup/Groups/Commission-Settings.md) directly in MetaTrader 5 based on the commission calculation formula used on the exchange.
  * FIX Drop Copy Address — address for connection to the MFIX Drop Copy service. The gateway can work without connection to the service. In that case, leave this parameter empty.
  * FIX Drop Copy TargetCompID — FIX messages heading standard parameter used for a message recipient identification for the MFIX Drop Copy service.
  * FIX Drop Copy SenderCompID — FIX messages heading standard parameter used for a message sender identification for the MFIX Drop Copy service.
  * FIX Drop Copy Password — password for connection to MFIX Drop Copy.
  * FIX Trade Capture Address — address for connection to MFIX Trade Capture.
  * FIX Trade Capture TargetCompID — FIX messages heading standard parameter used for a message recipient identification for the MFIX Trade Capture service.
  * FIX Trade Capture SenderCompID — FIX messages heading standard parameter used for a message sender identification for the MFIX Trade Capture service.
  * FIX Trade Capture Password — password for connection to the MFIX Trade Capture service.
  * Limits Url — local or FTP address of limit files to be imported to MetaTrader 5.
  * Limits Corrections Url — local or FTP address of limit correction files to be imported to MetaTrader 5.
  * Limits Corrections Result Url — local or FTP address where the files of limit correction import results will be exported.



> In order to download and import the limits and corrections, the gateway requires all three parameters filled: Limits Url, Limits Corrections Url and Limits Corrections Result Url. If any of them is not filled or absent, the gateway will not download and import the files.

  * Limits FTP Login — if limit files are received from the FTP server, specify the login and password for connection to it.
  * Limits FTP Password — if limit files are received from the FTP server, specify the login and password for connection to it.
  * Symbols Path \- path for importing the exchange symbols. By default, if this parameter is absent, the gateway imports the exchange's trading symbols to \MOEX\Securities\ subdirectory with trading ability disabled. A system administrator should allow trading for them after the import. If this parameter is present, the gateway imports trading symbols following the specified path.
  * Limits Kind — specify a type of limits imported from the limits file (Limits Kind = LIMIT_KIND from the file). For the securities market, the default value is "2" (corresponds to the T+2 limits).
  * Trades Mode — specify the markets (for example, TQBR, TQDE, TQIF) the gateway is to work for. The mode codes are used to define the markets. The values can be comma-separated or entered via the "*" and "!" masks. Do not specify the "*" mask (all markets) because the same instruments (the ones having similar names) with different quotes can be traded on different markets. In MetaTrader 5, symbol names are unique, and all quotes are merged into a single stream.
  * Execution Reports Mode — specify the markets, for which Execution Reports are processed. This parameter is reserved for future use. You do not need to specify it.
  * Short Limits Enabled — if "Yes", the gateway checks global limits by clients' short positions (by QUIK limit files). Brokers have certain assets for each trading instrument (for example, a certain number of shares). To avoid calculation issues, they should not allow their traders to sell more assets than they have. When the check is enabled, the gateway keeps internal statistics of short positions for each instrument opened by traders during the day. When reaching the limit, further requests for opening short positions are rejected. The gateway also considers traders' long deals — if a long position is opened after a short one for the same instrument and with the same volume, the limit returns to its original state. If only a long position is opened, the total limit is not increased.  
The gateway keeps an internal record of short positions during the session even if ShortLimitsEnabled is disabled. Thus, if the parameter is enabled during a trading session, the gateway does not need time for calculations. If the limit is already exceeded at the time of connection, further short operations are immediately rejected. By default, the check is disabled ("No").
  * FIX Heartbeat Interval — Heartbeat messages are used in the FIX protocol for monitoring the status of connection between the Exchange and the gateway. If the gateway does not receive any data from the Exchange or Heartbeat messages during the FIX Heartbeat Interval, the connection is considered to be lost and the gateway tries to restore it. The default value of FIX Heartbeat Interval is 30 seconds. The valid range of values is from 10 to 60 (the number of seconds).
  * External Account Required — if the external system account is not specified for the client on the MetaTrader 5 side, the client's requests are sent to the exchange on behalf of the broker, not on behalf of the client. To disable sending of requests from such clients to the exchange, set "Yes" for the External Account Required parameter. The gateway will immediately reject such requests. "No" is used by default, which means requests from clients without the external account are sent to the exchange.
  * Margin Calculation Mode — [calculation type (#calculation)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#calculation) used for the financial instruments imported by the gateway into the platform. If "Common", symbols are imported with the "Exchange Stocks" and "Exchange Bonds" types. If the value is "MOEX", symbols are imported with the "Exchange MOEX Stocks" and "Exchange MOEX Bonds" types (margin calculation is performed according to the rules adopted at the exchange on July 1st, 2019).
  * Time To Start — by default, the gateway starts connecting to the exchange's server 35 minutes before the start of the main trading session (9:25 GMT+3). Some brokers may need to change this parameter. To do this, use Time To Start parameter to specify in how many minutes before the session the gateway should start connection. For example, if connection is to start at 9:35, the parameter's value should be 25. The maximum possible value for the parameter is 250.
  * Money Currency Codes — currencies of money limits for which import from the limits file is allowed. The default is "SUR,USD": money limits for all currencies except the Russian Ruble and the US Dollar are skipped. The value corresponds to the "CURR_CODE" tag from the limits file.
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



> How to change password for FIX services

On the Groups tab, specify the group of clients who will trade in the FX Market. The gateway will only receive trade requests from the clients included in the allowed groups list.

![Configuring groups for MetaTrader 5 Gateway to MOEX Securities](images/moex_sec_groups.png)

To import the limits via the gateway, enable the "Allow importing traders balances" option. This will allow the gateway to synchronize clients' balances in MetaTrader 5 with exchange account limits.

> A group of clients trading in the FX Market should be configured correctly.

On the Symbols tab, specify the symbols available for the gateway. The gateway will receive quotes and perform trade operations for these symbols. Also, the settings will be automatically updated for them in case import of symbols is allowed:

![Configuring symbols for MetaTrader 5 Gateway to MOEX Securities](images/moex_sec_symbols.png)

Specify here the group of symbols the gateway will operate with. Also, "Allow importing symbol settings" should also be enabled. MetaTrader 5 Gateway to MOEX Securities adds necessary symbols and manages their settings on its own.

The symbols imported by the gateway are put to the "\MOEX\Securities" symbols subgroup.

> The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

<a id="group"></a>
## Configuration of groups (#group)

A separate group should be created for the clients working in the securities market. Specify RUR as the deposit currency in the group settings:

![Configuring a client group for trading in the securities market](images/moex_sec_group_common.png)

In the "Margin" tab, choose the risk management mode "for Stock Exchange, based on margin discount rates". In this mode, pre-trade control is based on discounts specified in [symbol settings](../../Platform-Setup/Symbols/Symbol-Settings/Margin-Rates.md). Discounts are set by the broker, however they cannot be lower than the values ​​determined by [National Clearing Centre](https://www.nkcbank.com/viewCatalog.do?menuKey=36) (NCC).

![Configuring a client group for trading in the securities market](images/moex_sec_group_margin.png)

For separate clients based on risk policies, create different groups for them. In these groups, [you can override symbol discount settings](../../Platform-Setup/Groups/Group-Symbol-Settings/Margin.md).

<a id="configuring-trade-requests-routing"></a>
## Configuring trade requests routing (#configuring-trade-requests-routing)

To direct client requests concerning the securities market symbols to the gateway, the [routing rules](../../Platform-Setup/Routing.md) should be set. The examples can be found in the articles about the gateways to other trading systems, like: [GBOT (#routing)](https://support.metaquotes.net/en/articles/332#routing), [DGCX (#routing)](https://support.metaquotes.net/en/articles/330#routing), etc.

<a id="account"></a>
## Configuring trading accounts (#account)

Each client on MetaTrader 5 side should be provided with a corresponding separate trading account on the exchange. After an account is opened at the exchange, it should be connected with the account within the platform. Open the appropriate client account and move to Account tab:

![Configuring the account](images/moex_sec_account.png)

A new entry should be added in "Trade accounts" section. Select MetaTrader 5 Gateway to MOEX Securities in "Gateway ID" field. Specify the client code in "Account" field (client code on the exchange).

> If the external system account is not specified for the client, the client's requests are sent to the exchange on behalf of the broker, not on behalf of the client. You may use the External Account Required parameter to disable sending of requests from such clients to the exchange.

<a id="the-configuration-of-the-gateway-is-complete-to-control-the-gateway-operation-use-the-journalplatform-setupgatewaysjournal-ofmd"></a>
## The configuration of the gateway is complete. To control the gateway operation, use the [Journal](../../Platform-Setup/Gateways/Journal-of.md). (#the-configuration-of-the-gateway-is-complete-to-control-the-gateway-operation-use-the-journalplatform-setupgatewaysjournal-ofmd)

<a id="gateway-launch-specifics"></a>
## Gateway launch specifics (#gateway-launch-specifics)

To avoid an excessive load, the amount of attempts to connect the gateway to the exchange is limited. If the gateway is unable to connect the exchange immediately, it repeats connection attempts for approximately 5 minutes (about 15 attempts). If all the attempts fail, the gateway stops and writes the following entry in the journal:

reached the maximum number of connection attempts (16), gateway stopped  
---  
  
In order for the gateway to continue connection attempts, the administrator should restart the gateway.

<a id="quotes-only"></a>
## Running in Quote Receiving Mode (#quotes-only)

This mode allows using the gateway only for receiving quotes from the exchange, without processing trading operations. Leave the value of the following parameters blank:

  * Trade server
  * FIX Drop Copy Address
  * FIX Trade Capture Address



The gateway will only connect to FAST channels to receive a list of symbols and quotes.

> In this mode, the gateway continues processing limit files, but does not process correction files.

<a id="operations"></a>
## Gateway Service Operations (#operations)

The gateway can perform various service operations on accounts during operation.

  * Deals with the type "Correction" and with the comment "[synchronization]" are formed when synchronizing limits of the account with the QUIK limit file
  * Deals with the comment "limit correction, 'XXXXX'" are formed when limits are corrected according to the corresponding QUIK file
  * Deals with the comment "[swap close deal]" and "[swap reopen deal]" are formed when processing a swap deal arriving though the Trade Capture channel
  * Deals with the comment "[target repo leg 1]" and "[target repo leg 2]" are formed when processing a targeted repo trade arriving through the Trade Capture channel on the Securities Market
  * Deals with the comment "[target deal]" are formed when processing a targeted deal arriving through the Trade Capture channel on the Securities Market
  * Deals with the comment "[repo leg 1]" and "[repo leg 2]" are formed when processing a targeted repo trade arriving through the Trade Capture channel on the Securities Market
  * Deals with the comment "[technical deal]" are formed when processing a technical deal on the Securities Market



```

---

<a id='gateways-moexfx-md'></a>
### 119. `Gateways/MOEXFX.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / MOEXFX

[Previous](../Gateways.md) | [Next](MOEX-Securities.md)

<a id="metatrader-5-gateway-to-moexfx"></a>
# MetaTrader 5 Gateway to MOEXFX (#metatrader-5-gateway-to-moexfx)

MetaTrader 5 Gateway to MOEXFX enables one-click currency trading with the exchange "Depth Of Market" option and financial market analysis using built-in technical indicators. With the wide functionality of MetaTrader 5, traders can automate the trading process using robots, which they can develop themselves, order from professionals or buy in the trading application store [MetaTrader Market](https://www.mql5.com/en/market). Financial news and important releases appear right in the terminal to enable traders keep the track of market events. The extremely popular market service of [Copy Trading](https://www.mql5.com/en/signals) is also available to traders.

[Moscow Exchange's FX Market](https://moex.com/s1094) is the oldest regulated domestic FX trading venue operating since 1992. The Exchange market is the center of liquidity for ruble related operations. The Bank of Russia sets the official ruble exchange rate on the basis of exchange trading results.

Moscow Exchange's FX Market is one of the most dynamically developing segments of Russia's financial market. The total trading volume on Moscow Exchange's FX Market increased 34% YoY and amounted to 156 trln rubles in 2013. Now Moscow Exchange is experiencing increased activity: in the third quarter of 2014 [trading volumes increased](https://moex.com/n6803/?nt=201) in almost all markets, but the FX section showed the best result. The total trading volume of the FX Market has increased by 26.4% compared to the third quarter of 2013 and amounted to 55.86 trillion rubles.

USD, Euro, Chinese Yuan, Ukrainian hryvnia, Kazakh tenge, the Belarusian ruble, bi-currency basket, and FX swap transactions can be made via the market's electronic trading system.

> [Order MetaTrader 5 Gateway to MOEXFX](https://support.metaquotes.net/en/market/product/272)

<a id="general"></a>
## Common Trading Principles and their Implementation in MetaTrader 5 (#general)

Trading in the FX Market is regulated by ["FX and Precious Metals Market Trading Rules of the Moscow Exchange"](https://fs.moex.com/files/1498). Here are some of the key trading features and examples.

In the currency market, the result of a transaction is immediately shown on the client trading status. By opening a long position, a client receives assets, while obligations arise from opening a short position.

At this point MetaTrader 5 provides two types of financial instruments of Moscow Exchange's FX Market:

  * Settlement of obligations is due on the day of the transaction. Suffix TOD is used for such instruments. For example, USDRUB_TOD. Each TOD symbol is traded during a certain session defined by the Exchange trading hours, obligations are settled at the end of the sessions. For example, USDRUB_TOD trading hours are 10:00 to 17:15 (Moscow time).
  * Settlement of obligations is due on the day following the day of the transaction. Suffix TOM is used for such instruments. For example, USDRUB_TOM. TOM instruments are traded 10:00 to 23:50 (Moscow time). At the end of the trading session, all positions of TOM instruments turn into positions of TOD instruments. If there are TOD positions on the account in addition to the TOD positions, they are consolidated (position netting).



Consider opening a short and a long position of 1 lot for USDRUB_TOD at the price of 52 RUR, the contract size is 1,000.

Position Opening

  * Short — when a short position is opened, the client's obligation is to sell 1,000 of his US dollars for rubles at the price of the transaction.
  * Long — when a long position is opened, the client's obligation is to buy 1,000 US dollars for rubles at the price of the transaction.



Margin Trading

Trade is marginal and contractual obligations are delayed in time. Until the time of settlement of obligations, the margin is locked on the client's account. The margin is defined by [discounts](../../Platform-Setup/Symbols/Symbol-Settings/Margin-Rates.md) relative to the current price of the instrument. Discounts are set by the broker, however they cannot be lower than the values set by [National Clearing Centre](https://www.nkcbank.ru/) (NCC). Due to the discounts, clients can make transactions with a leverage, i.e. traders can open positions investing a larger sum than is available on their account.

Fulfillment of Obligations and Swap Operations

At the time of settlement, the broker takes the client's obligation in the fullest possible volume. If money on the client's account is not enough to settle a liability, then a swap transaction is conducted at the amount of the remaining position. Consider the examples of short and long positions.

  * Long position — the client has purchased 1,000 USD at 52 RUR. Thus, during settlement the client needs to take US dollars and pay 52,000 RUR. However, at the time of payment the client has only 30,000 RUR, so part of the position is uncovered. This part is swapped. The part of the position for which obligation was settled becomes a settled position - client's asset, its value at the current rate with [liquidity ratio](../../Platform-Setup/Symbols/Symbol-Settings/Margin-Rates.md) correction can be used as collateral for opening new positions.
  * Short position — the client is obligated to sell his own 1,000 USD at 52 RUR. If the required currency amount is not available on the trader's account, the broker is committed to supply the required amount. This is a swap operation.



A swap consists of two transactions: the current position is closed and is re-opened for the appropriate TOM instrument. The difference between the position close price and the re-open price is called the "swap" price, it is determined by the broker's interest rate.

Thus, a trader can have two types of positions:

  * Unsettled position — the positions, for which the trader expects the settlement of obligations.
  * Settled positions — client's assets.



For customer convenience and ease of calculation, these positions are not differentiated in MetaTrader 5. The settled positions are displayed in the form of unsettled positions of corresponding TOD instruments.

<a id="principles"></a>
## How the Gateway Works (#principles)

MetaTrader 5 Gateway to MOEXFX is a separate "MOEXFXGateway64.exe" file that uses Gateway API for operation. Gateway module is originally included in the platform delivery set. After purchasing the gateway, the trading platform license will automatically update via LiveUpdate system. This allows you to start using MetaTrader 5 Gateway to MOEXFX without any limitations.

The gateway receives market data of trading on Moscow Exchange via Multicast. This is a UDP protocol that allows packets to be transmitted to multiple recipients. Find the details of the protocol in ["Market Data Multicast Ver3.3 User Guide"](https://ftp.micex.com/pub/FAST/ASTS/docs/Archive/Eng_Market_Data_Multicast_User_Guide_Ver3.3.3.pdf). The system administrator must configure the server where the gateway is running to receive data.

The UDP protocol does not have built-in methods to ensure reliability, ordering, or data integrity, which on the one hand makes it unreliable. But on the other hand, it saves time required to deliver data to clients. This provides data delivery to clients with minimum delay. All transmitted data are doubled to control the integrity of transmitted data. The gateway receives market data from the Exchange in four tables:

  * Trades executed on the Exchange.
  * Trade statistics.
  * Depth of Market.
  * List of instruments.



To deliver each data type, four connections are created: two connections for the incremental channel where only changes relative to the previous state are transmitted, and two for the snapshots (the state at a certain time).

For committing trade operations and receiving the trading status of clients, the gateway uses three FIX services, for each of which a separate connection is created:

  * MFIX Trade — entering and canceling orders and receiving order execution reports.
  * MFIX Drop Copy — receiving the stream of orders and deals from other terminals (other than MetaTrader 5).
  * MFIX Trade Capture — sending all trades of all accounts bound to the current FIX identifier of the broker.



Accordingly, three FIX IDs are required. Read more about the FIX services in ["Moscow Exchange public FIX 4.4 interface specification for Securities and FX markets"](ftp://ftp.micex.com/pub/FIX/ASTS/docs/public_fix44_interface_in_eng_v_4.pdf). If any of the FIX services is not required, it can be omitted. Simply do not specify its address in the gateway settings.

<a id="integration"></a>
## Integration with Broker's Back Office (#integration)

The relevant trading client state in MetaTrader 5 is maintained using the client limiting interface provided by the gateway. Limiting is implemented through import of limit files in the QUIK format. The detailed format description is available in the [QUIK WorkStation](https://www.quik.ru/depot/quikref_eng.zip) reference. This format is used due to the fact that most of the brokers that provide access to Moscow Exchange have this platform, and therefore such an approach is the most simple and convenient one to move to MetaTrader 5.

In [the gateway settings (#param)](MOEXFX.md#param) specify the address (ftp or local address), from which the gateway shall automatically read the limit and correction files and synchronize client states in MetaTrader 5. The limit file can be used at any moment of gateway operation. Once the administrator adds a file to the specified directory, the gateway will process it and will set the client status in accordance with it. This behavior can also be used to recover client states in case of failure.

Limit correction files are used to reflect the limit changes in the broker's back-office system. The gateway processes them only during trading hours (10:00 to 23:50 Moscow time). Correction files are processed in accordance with the following algorithm:

  * When the correction file is updated, the gateway starts analyzing it.
  * It parses all the correction entries from the file one by one.
  * The gateway finds the entry with LIMIT_ID (the correction identifier is unique within a file for one trading day) equal to LIMIT_ID_LAST (the identifier of the last processed correction).
  * All subsequent entries are processed and applied to client trading status. While each subsequent entry is processed, the value of LIMIT_ID_LAST is updated to avoid repeated correction.
  * As soon as processing is over, the gateway uploads the file with the correction results. The file is of the QUIK system format. The file is uploaded at the address specified in the [gateway settings (#param)](MOEXFX.md#param).
  * At the beginning of each trading day, the ID of the last processed correction is reset.



<a id="configuring-the-gateway"></a>
## Configuring the Gateway (#configuring-the-gateway)

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway Connection Settings](images/moex_fx_common.png)

The following parameters on the "Common" tab must be configured:

  * Module — MOEXFXGateway64. After selection, use of the gateway default parameters must be allowed in the dialog request.
  * ID — unique dealer identifier, on whose behalf the trade requests will be processed. Requests are routed to the gateway according to this identifier.
  * Trading server — address for connection to the MFIX Trade service.
  * Trading login — login (FIXTradeSenderCompID) for connection to MFIX Trade.
  * Password — password for connection to MFIX Trade.



  * ID value must be unique in the field of manager logins and gateway identifiers.
  * Connection data (address, login and password) are provided by the exchange.

  
---  
  
Additional configuration parameters must be set on the Parameters tab:

![MetaTrader 5 Gateway to MOEXFX Parameters](images/moex_fx_param.png)

The following additional parameters are available for the gateway:

  * Trading Calendar Holidays — each exchange works in accordance with its own trading calendar. By default, non-working days for the gateway are Saturday and Sunday. Using this option, you can override the working/non-working days for the gateway. To add a non-working day, specify a value of the form +DDMMM. The date is specified as two digits, the month is specified as the first three letters of the month name in English. For example, +01JAN. To add a working day on Saturday or Sunday, specify a value of type -DDMMM, for example, -07FEB. You can specify multiple working/non-working days separated by semicolons, for example, + 01JAN;-07FEB.
  * Market Feed ConfigUrl — parameters of channels for receiving market data from the exchange are described in the XML file. This file is available on the [Exchange's FTP server](https://ftp.micex.com/pub/FAST/ASTS/config/). Specify the path to the file depending on what data you want to receive (real or test). Configuration file can be copied to a local server, the appropriate path should be specified in this field. The gateway reads data for connection to the following channels (set by the connection_id parameter in the file):


  *     * OBR and OBS — an incremental channel and a channel of snapshots for transmitting the depth of market.
    * TLR and TLS — an incremental channel and a channel of snapshots for transmitting trading operations.
    * MSR and MSS — an incremental channel and a channel of snapshots for transmitting trade statistics.
    * IDF — a channel for transmitting the list of financial instruments.
  * Market Feed FAST Templates Url — all market data are transmitted through the FAST protocol. Transmitted data are unpacked using the special FAST template. Specify here the path to the template file, it is available on the [Exchange's FTP server](https://ftp.micex.com/pub/FAST/ASTS/template/). You can specify the FTP path or copy the file to a local server and specify the appropriate local path to it.



> Market channel parameters and template files downloaded via FTP are saved in the directory [gateway folder]\downloads. If the gateway fails to download updated files, it will use earlier downloaded files stored in this folder. The following rules apply here:

  * Market Feed A Bind — the address of the local interface the connection will be bound to in order to receive market data through channel A (all data from the Exchange are duplicated on two channels).
  * Market Feed B Bind — the address of the local interface the connection will be bound to in order to receive market data through channel B (all data from the Exchange are duplicated on two channels).
  * Trade Account — the account used for registering the transaction performed through the gateway on the Exchange.
  * Trade Commission Use — this parameter sets the use of commissions from the Exchange. The commissions are specified in each transaction received from the Exchange. If the parameter is set to "Yes", this value is used in the platform. If set to "No" (default), the broker can configure [commission calculation](../../Platform-Setup/Groups/Commission-Settings.md) directly in MetaTrader 5 based on the commission calculation formula used on the Exchange.
  * FIX Trade TargetCompID — FIX messages heading standard parameter used for a message recipient identification for the MFIX Trade service. The remaining connection parameters are specified on the "Common" tab in the gateway settings.
  * FIX Drop Copy Address — address for connection to the MFIX Drop Copy service. The gateway can work without connection to the service. In that case, leave this parameter empty.
  * FIX Drop Copy TargetCompID — FIX messages heading standard parameter used for a message recipient identification for the MFIX Drop Copy service.
  * FIX Drop Copy SenderCompID — FIX messages heading standard parameter used for a message sender identification for the MFIX Drop Copy service.
  * FIX Drop Copy Password — password for connection to MFIX Drop Copy.
  * FIX Trade Capture Address — address for connection to MFIX Trade Capture.
  * FIX Trade Capture TargetCompID — FIX messages heading standard parameter used for a message recipient identification for the MFIX Trade Capture service.
  * FIX Trade Capture SenderCompID — FIX messages heading standard parameter used for a message sender identification for the MFIX Trade Capture service.
  * FIX Trade Capture Password — password for connection to the MFIX Trade Capture service.
  * Limits Url — local or FTP address of [limit (#integration)](MOEXFX.md#integration) filed to be imported to MetaTrader 5.
  * Limits Corrections Url — local or FTP address of limit correction files to be imported to MetaTrader 5.
  * Limits Corrections Result Url — local or FTP address where the files of limit correction import results will be exported.



> In order to download and import the limits and corrections, the gateway requires all three parameters filled: Limits Url, Limits Corrections Url and Limits Corrections Result Url. If any of them is not filled or absent, the gateway will not download and import the files.

  * Limits FTP Login — if limit files are received from the FTP server, specify the login and password for connection to it.
  * Limits FTP Password — if limit files are received from the FTP server, specify the login and password for connection to it.
  * Symbols Path — path for importing the exchange symbols. By default, if this parameter is absent, the gateway imports the exchange's trading symbols to \MOEX\FX\ subdirectory with trading ability disabled. A system administrator should manually allow trading for them. If this parameter is present, the gateway imports trading symbols following the specified path.
  * Limits Kind — this parameter is used for specifying a type of limits imported from the limits file (Limits Kind = LIMIT_KIND from the file). For the foreign exchange market, the default value is "0" (corresponds to the T+0 limits).
  * Trades Mode — this parameter specifies the markets (for example, auction, repo deals, target deals) the gateway should work for. The mode codes are used to define the markets. The values can be comma-separated or entered via the "*" and "!" masks.
  * Execution Reports Mode — this parameter specifies the markets, for which Execution Reports are processed. This parameter is reserved for future use. You do not need to specify it.
  * Limits Sync Exclude — allows disabling synchronization of positions and balances for the specified client groups. The platform allows transmitting trading operations from one account through different gateways. To do this, multiple accounts in external systems corresponding to different gateways are registered in the account. There are three gateways for the Moscow Exchange. Each of them synchronizes the trading state and limits. The possibility to disable synchronization allows to prevent overwriting of data about positions and limits during simultaneous operation through these gateways. Specify the list of groups for which the gateway should not synchronize positions and balances in this parameter. Groups can be specified using the "*" mask.
  * FIX Heartbeat Interval — Heartbeat messages are used in the FIX protocol for monitoring the status of connection between the Exchange and the gateway. If the gateway does not receive any data from the Exchange or Heartbeat messages during the FIX Heartbeat Interval, the connection is considered to be lost and the gateway tries to restore it. The default value of FIX Heartbeat Interval is 30 seconds. The valid range of values is from 10 to 60 (the number of seconds).
  * External Account Required — if the [external system account (#account)](MOEXFX.md#account) is not specified for the client on the MetaTrader 5 side, the client's requests are sent to the exchange on behalf of the broker, not on behalf of the client. To disable sending of requests from such clients to the exchange, set "Yes" for the External Account Required parameter. The gateway will immediately reject such requests. "No" is used by default, which means requests from clients without the external account are sent to the exchange.
  * Margin Calculation Mode — [calculation type (#calculation)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#calculation) used for the financial instruments imported by the gateway into the platform. If "Common", symbols are imported with the "Exchange Stocks" type. If the value is "MOEX", symbols are imported with the "Exchange MOEX Stocks" type (margin calculation is performed according to the rules adopted at the exchange on July 1st, 2019).
  * Time To Start — by default, the gateway starts connecting to the exchange's server 70 minutes before the start of the main trading session (05:50 GMT+3). Some brokers may need to change this parameter. To do this, use Time To Start parameter to specify in how many minutes before the session the gateway should start connection. For example, if connection is to start at 6:00, the parameter's value should be 60. The maximum possible value for the parameter is 70.
  * Money Currency Codes — currencies of money limits for which import from the limits file is allowed. The default is "SUR,USD": money limits for all currencies except the Russian Ruble and the US Dollar are skipped. The value corresponds to the "CURR_CODE" tag from the limits file.
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



> How to Change Password for FIX Services

On the Groups tab, specify the group of clients who will trade in the FX Market. The gateway will only receive trade requests from the clients included into the allowed groups list.

![Configuring Groups for MetaTrader 5 Gateway to MOEXFX](images/moex_fx_groups.png)

To import the limits via the gateway, enable the "Allow importing traders balances" option. This will allow the gateway to synchronize clients' balances in MetaTrader 5 with exchange account limits.

> Make sure to [configure (#group)](MOEXFX.md#group) the group of clients trading in the FX Market correctly.

On the Symbols tab, specify the symbols available for the gateway. The gateway will receive quotes and perform trade operations for these symbols. Also, the settings will be automatically updated for them in case import of symbols is allowed:

![Configuring Symbols for MetaTrader 5 Gateway to MOEXFX](images/moex_fx_symbols.png)

Specify here the group of symbols the gateway will operate with. Also, "Allow importing symbol settings" should also be enabled. MetaTrader 5 Gateway to MOEXFX adds necessary symbols and manages their settings on its own. 

The symbols imported by the gateway are put to the "\MOEX\FX" symbols subgroup.

> The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

<a id="group"></a>
## Configuration of Groups (#group)

Create a separate group for the clients working in the FX market. Specify RUR as the deposit currency in the group settings:

![Configuring a Client Group for Trading in the FX Market](images/moex_fx_group_common.png)

In the "Margin" tab choose the risk management mode "for Stock Exchange, based on margin discount rates". In this mode, pre-trade control is based on discounts specified in [symbol settings](../../Platform-Setup/Symbols/Symbol-Settings/Margin-Rates.md). Discounts are set by the broker, however they cannot be lower than the values ​​determined by [National Clearing Centre](https://www.nkcbank.ru/) (NCC).

![Configuring a Client Group for Trading in the FX Market](images/moex_fx_group_margin.png)

To separate clients based on risk policies, create different groups for them. In these groups you can [override symbol discount settings](../../Platform-Setup/Groups/Group-Symbol-Settings/Margin.md).

<a id="configuring-trade-requests-routing"></a>
## Configuring Trade Requests Routing (#configuring-trade-requests-routing)

To forward client requests concerning FX Market symbols to the gateway, the [routing rules](../../Platform-Setup/Routing.md) should be set. Examples can be found in the articles concerning the gateways to other trading systems, for example: [GBOT (#routing)](https://support.metaquotes.net/en/articles/332#routing), [DGCX (#routing)](https://support.metaquotes.net/en/articles/330#routing), etc.

<a id="account"></a>
## Configuring Trading Accounts (#account)

Each client on MetaTrader side should be provided with a corresponding separate trading account on the exchange. After an account is opened at the exchange, it should be connected with the account within the platform. Open the appropriate client account and move to Account tab:

![Configuring the account](images/moex_fx_account.png)

A new entry should be added in "Trade accounts" section. Select MetaTrader 5 Gateway to MOEXFX in "Gateway ID" field. Specify the client code in "Account" field (client code on the exchange).

> If the external system account is not specified for the client, the client's requests are sent to the exchange on behalf of the broker, not on behalf of the client. You may use the [External Account Required (#externalaccountrequired)](MOEXFX.md#externalaccountrequired) parameter to disable sending of requests from such clients to the exchange.

The configuration of the gateway is complete. To control the gateway operation use the [journal](../../Platform-Setup/Gateways/Journal-of.md).

<a id="gateway-launch-specifics"></a>
## Gateway Launch Specifics (#gateway-launch-specifics)

To avoid an excessive load, the amount of attempts to connect the gateway to the exchange is limited. If the gateway is unable to connect the exchange immediately, it repeats connection attempts for approximately 5 minutes (about 15 attempts). If all the attempts fail, the gateway stops and writes the following entry in the journal:

reached the maximum number of connection attempts (16), gateway stopped  
---  
  
In order for the gateway to continue connection attempts, restart the gateway.

<a id="auction"></a>
## Discrete Auction Mode (#auction)

Discrete auction mode of trading the USDRUB pair can be launched on Moscow Exchange in case of ultra-high volatility. In this mode, USDRUB_TOM trading stops and trading on the special USDRUB_DIS symbol begins. To ensure the continuity of the trading process on the MetaTrader 5 side, a mechanism for automated mapping of quotes and trading operations between these symbols has been implemented in the gateway.

During the auction, all USDRUB_TOM orders placed on the MetaTrader 5 side will be sent to the exchange as USDRUB_DIS orders. All USDRUB_DIS quotes provided by the exchange will be passed to the platform as USDRUB_TOM quotes.

The start and stop of the discrete auction is displayed in the gateway log:

2018.04.18 12:37:00.355 Gateway discrete auction is started, name exchange: USDRUB_TOM, name gateway: USDRUB_DIS  
2018.04.18 12:52:03.157 Gateway discrete auction is stopped, name exchange: USDRUB_DIS, name gateway: USDRUB_TOM  
---  
  
During the discrete auction time, all Stop Loss and Take Profit triggers for the USDRUB_TOM instrument are rejected, in order to avoid closure of clients' positions by bids from the auction Market Depth. The following message is printed to the log in this case:

request rejected, because SL and TP are discarded during a discrete auction  
---  
  
Also, Stop orders on USDRUB_TOM will not trigger during the auction.

<a id="quotes-only"></a>
## Running in Quote Receiving Mode (#quotes-only)

This mode allows using the gateway only for receiving quotes from the exchange, without processing trading operations. Leave the value of the following [parameters (#param)](MOEXFX.md#param) blank:

  * Trade server
  * FIX Drop Copy Address
  * FIX Trade Capture Address



The gateway will only connect to FAST channels to receive a list of symbols and quotes.

> In this mode, the gateway continues processing limit files, but does not process correction files.

<a id="operations"></a>
## Gateway Service Operations (#operations)

The gateway can perform various service operations on accounts during operation.

  * Deals with the type "Correction" and with the comment "[synchronization]" are formed when [synchronizing limits (#integration)](MOEXFX.md#integration) of the account with the QUIK limit file
  * Deals with the comment "limit correction, 'XXXXX'" are formed when limits are corrected according to the corresponding QUIK file
  * Deals with the comment "[swap close deal]" and "[swap reopen deal]" are formed when processing a swap deal arriving though the [Trade Capture (#fixtradecaptureaddress)](MOEXFX.md#fixtradecaptureaddress) channel
  * Deals with the comment "[auction]" are formed when processing a deal executed during an [auction (#auction)](MOEXFX.md#auction)
  * Deals with the comment "[technical deal]" are formed when processing a technical deal on the market



```

---

<a id='gateways-metatrader-4-md'></a>
### 119. `Gateways/MetaTrader-4.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / MetaTrader 4

[Previous](MetaTrader-5.md) | [Next](Integral.md)

<a id="metatrader-5-gateway-to-metatrader-4"></a>
# MetaTrader 5 Gateway to MetaTrader 4 (#metatrader-5-gateway-to-metatrader-4)

The gateway allows any brokerage firm to integrate with larger brokers and liquidity providers using the MetaTrader 4 trading platform. You will be able to minimize your risk and receive potential profit from each trade operation of a client due to markups. All you need to do is select a liquidity provider and perform a simple gateway configuration.

> [Order MetaTrader 5 Gateway to MetaTrader 4](https://support.metaquotes.net/en/market/product/267)

<a id="how-the-gateway-works"></a>
## How the Gateway Works (#how-the-gateway-works)

The gateway acts as an intermediary between the two platforms by converting trade requests of brokerage clients into requests to the external MetaTrader 4 trading platform, receiving answers and sending them back to clients.

The [routing rules (#routing)](MetaTrader-4.md#routing) allow configuring the broker's server in such a way that the clients' trade requests are sent to the gateway. Depending on the order type, each request is handled differently:

  * Market orders are passed to the gateway directly.
  * All pending orders are not passed to the gateway by default. They are handled within the trading platform instead. An appropriate market request is sent to the gateway immediately after activation.
  * Take Profit, Stop Loss and Stop Out orders are handled and stored on the MetaTrader 5 platform side. The appropriate market operation is sent to the external platform right after activation.



  * The gateway is already included in the MetaTrader 5 platform and can be used in demo mode, which allows performing not more than 100 trading operations for a work session (until restart). The full version should be purchased separately.
  * The gateway transmits quotes from the external MetaTrader 4 platform.

  
---  
  
<a id="wl"></a>
## Requirements (#wl)

For proper operation of the gateway and correct accounting of funds, it is necessary to ensure that the symbol on the broker's server have the same trading settings as the remote MetaTrader 4 platform. The symbol's trading parameters can be set in the symbols setup dialog. The following symbol settings should be the same:

  * The mode of [order execution](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md) by a symbol
  * [Number of digits](../../Platform-Setup/Symbols/Symbol-Settings/Common.md) after the decimal point
  * [Type of calculation (#calculation)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#calculation) of margin requirements and profit on a symbol
  * [The price of one point](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md) of the price change, except for instruments with the Forex calculation mode
  * [Size of one point](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md), except for instruments with the Forex calculation mode
  * For the Request execution mode, the [mode of order confirmation](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md) should be enabled



> A trade account should be created on MetaTrader 4 external server, on behalf of which all client trade operations passed through the gateway are performed.

<a id="gateway-configuration"></a>
## Gateway Configuration (#gateway-configuration)

MetaTrader 5 Gateway to MetaTrader 4 is a separate MetaTrader4Gateway64.exe file that uses Gateway API for its operation. The gateway is distributed as part of the MetaTrader 5 platform and located in [history server installation directory]\gateway\\.

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Configuring the gateway](images/mt4gateway_common.png)

Set the following parameters on the "Common" tab:

  * ID — set the identifier of the dealer, from whose name the requests routed to the gateway are confirmed.
  * Module — select MetaTrader4Gateway64 in the list of available modules and load its default settings.
  * Trading server — MetaTrader 4 external server IP address and port trade requests are sent to.
  * Trading login — index of a trade account opened at MetaTrader 4 external server. This is the account, at which client trading operations passed through the gateway are performed.
  * Password — password for connecting to an account at MetaTrader 4 external server.



> ID value must be unique in the field of manager logins and gateway identifiers. Usually, this field is filled out automatically by an acceptable default value.

Now, go to the "Parameters" tab.

![Gateway parameters](images/mt4gateway_param.png)

The following additional parameters are available for the gateway:

  * Quotes Time Original — if the value is Yes, the gateway sets the time of ticks on its own considering a time zone of a recipient trading server. If No, or the parameter is absent, the time of ticks is set by the history server according to its own trading time.
  * News Category — the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Delay — delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample — the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample — the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample — the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



Use the Groups tab to select the group of clients, whose orders and positions will be available to the gateway.

![Configuring the groups](images/mt4gateway_groups.png)

The Symbols tab allows you to configure the list of symbols, according to which the gateway will process trade operations and transmit the quotes.

![Configuring the symbols](images/mt4gateway_symbols.png)

MetaTrader 5 Gateway to MetaTrader 4 supports the import of symbols and their settings from an external trading server. If the option "Allow importing symbol settings" is enabled, the import of symbols from an external server will be performed. All symbols available for an account used for connection (specified in "Trading server" field of the Common tab) are imported. The symbols are imported to Symbols/Preliminary/ subgroup according to their hierarchy at the external server.

  * The symbols imported by the gateway are put to the \Preliminary symbols subgroup. All symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After symbols are relocated and trading abilities are enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the existing symbol settings are not updated. Configuration of such a symbol is skipped.



> The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

<a id="routing"></a>
## Configuring trade requests routing (#routing)

After adding a new gateway, configure [routing](../../Platform-Setup/Routing.md) so that the clients' requests are routed to this gateway. Select "Process to dealers" as an action in the common rule settings. Assign this routing rule for all requests and orders. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

![Configuring routing](images/mt4gateway_routing.png)

Add the previously created gateway at the Dealers tab.

After the correct execution of the steps described above, the gateway is launched and ready to work. The result of the gateway operation is reflected in its [journal](../../Platform-Setup/Gateways/Journal-of.md).

<a id="markup"></a>
## Formation and Correction of Prices (#markup)

MetaTrader 5 Gateway to MetaTrader 4 translates the price flow from an external MetaTrader 5 platform, just like the data feeds do. The priority of quotes from the gateway is higher than the priority of quotes from a data feed. If quotes for a symbol are available both from the gateway and data feed, a client will receive the quotes from the gateway.

The gateway performs all trading operations considering the price correction. To set correction for each individual symbol, go to the Translations tab in the gateway settings and enter the appropriate values:

![Correction parameters](images/mt4gateway_translations.png)

In this example, the following corrections are specified for EURUSD: for each tick the Bid price will be reduced by 3 points, and the Ask price will be increased by 3 points.

A price is given to the broker's client only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices of the liquidity provider.

<a id="example"></a>
## Example (#example)

All trade operations performed by the gateway are included in the gateway journal. For example, using the client terminal we buy EURUSD 1.0. After processing the request, the following entries will appear in the journal of the MetaTrader 5 Gateway:

'1002': request #1179132 received (#2073 instant buy 1.00 EURUSD at 1.31237)  
'1002': request #1179132 answered - Done at 1.312370 (#1002 instant buy 1.00 EURUSD at 1.31237)(based on #2448959, #2448959, 1.31198 / 1.31212)  
---  
  
Let's consider the contents of the logs in more detail.

A request with the ID # 1179132 is received from the broker's client with the account 1002. Corresponding to this request, on the broker's server there is the client's order with the ID # 2073 to Buy one lot of EURUSD at the price of 1.31237.

To the request ID #1179132, the broker's client with the account 1002 receives a reply that the request has been executed (Done), with the request execution price 1.312370. In addition, the original order of the client is specified. The last part of the message contains the parameters of the trading operation on the remote platform. In particular, upon the client's request, generated order # 2448959, deal # 2448959, with the actual execution prices: Sell - 1.31198, Buy - 1.31212. In this case, this means that the client's Buy has been executed at 1.31212 on the external trading platform.

On this basis, we can calculate the profit from the price difference:

The broker's profit = 1.31237 - 1.31212 = 0.00025.

<a id="simulating-the-netting-accounting-system-on-metatrader-4"></a>
## Simulating the Netting Accounting System on MetaTrader 4 (#simulating-the-netting-accounting-system-on-metatrader-4)

MetaTrader 4 trading platform supports only the [hedging accounting system (#hedging)](../../Platform-Setup/Groups/Position-Accounting-Systems.md#hedging). This system allows you to have unlimited number of trading positions on a single financial instrument. In addition to hedging, MetaTrader 5 supports the [netting (#netting)](../../Platform-Setup/Groups/Position-Accounting-Systems.md#netting) system. This system is used on exchanges allowing a trader to have only one cumulative position at a symbol. Making a trade on the same instrument may change the existing position's volume, close it completely or reverse it.

If netting is used on MetaTrader 5 side, the gateway will try to simulate it on MetaTrader 4 external server.

The gateway automatically assigns an identification number to an account in the external server in the account settings of each client whose trades are passed to the external server (in case the number has not been already specified manually).

![ID in the external system](images/mt4gateway_external.png)

The ID is used as a magic number for all client orders (positions) passed to the external system. When a client's market transaction is sent to the MetaTrader 4 external server, the gateway additionally sends the command to close all opposite positions (Multiple close by) with the same magic number on the same symbol. Thus, only one resulting position remains at the external system for a single symbol.

```

---

<a id='gateways-metatrader-5-md'></a>
### 119. `Gateways/MetaTrader-5.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Gateways](../Gateways.md) / MetaTrader 5

[Previous](DGCX.md) | [Next](MetaTrader-4.md)

<a id="metatrader-5-gateway-to-metatrader-5"></a>
# MetaTrader 5 Gateway to MetaTrader 5 (#metatrader-5-gateway-to-metatrader-5)

The MetaTrader 5 Gateway is a gateway that allows bringing up trade operations to external MetaTrader 5 servers. Trade operations performed on the server will be processed and stored in an external system. Interaction between the platforms is performed through a client connection.

> [Order MetaTrader 5 Gateway to MetaTrader 5](https://support.metaquotes.net/en/market/product/266)

<a id="how-the-gateway-works"></a>
## How the Gateway works (#how-the-gateway-works)

The main task of the MetaTrader 5 gateway is to convert trade requests of a broker's clients into requests to the external MetaTrader 5 trading platform.

![Gateway operation scheme](images/mt5gateway_scheme.png)

All the requests of the broker's clients are translated to the liquidity provider. The response from the liquidity provider is transmitted to the client. The broker's server is configured in such a way that the clients' trade requests are sent to the MetaTrader 5 gateway. The gateway checks the clients' requests and after the successful check creates new trade requests to a remote platform. After receiving a response from the remote MetaTrader 5 platform, the gateway returns a response to the client's request to the broker's server.

<a id="trading-operations"></a>
### Trading Operations (#trading-operations)

Orders are sent to MetaTrader 5 Gateway to MetaTrader 5 for processing in accordance with the set [routing rules (#routing)](MetaTrader-5.md#routing). Depending on the order type, each request is handled differently:

  * Market orders are transferred to the gateway directly.
  * Limit orders are not transferred to the gateway by default. They are handled within the trading platform instead. An appropriate market request is sent to the gateway immediately after activation. Limit orders output mode can be changed using [Limit Orders Coverage Mode (#parameters)](MetaTrader-5.md#parameters) parameter in the gateway settings.
  * Stop orders are not transferred to the gateway immediately. Such orders are handled and stored on the MetaTrader 5 platform side. They stay in the MetaTrader 5 platform until a specified price level is reached. An appropriate market order is sent to the external system immediately after reaching this level.
  * Stop-limit orders are handled and stored on the MetaTrader 5 platform side. Such orders stay in the MetaTrader 5 platform until their stop price is reached. Once it has been reached, the corresponding limit order with a specified price will be created in MetaTrader 5 or sent to an external server depending on the [gateway settings (#parameters)](MetaTrader-5.md#parameters).
  * Take Profit, Stop Loss and Stop Out orders are handled and stored on the MetaTrader 5 platform side. An appropriate trading request is sent to an external platform immediately after the order triggering.



> The gateway handles operations on symbols with [Market Execution](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md) mode similar to exchange execution symbols. Handling does not depend on how operations are actually executed on the external server â in the market or exchange execution mode.

<a id="the-gateway-translates-only-to-the-external-system-only-the-requests-that-are-lossless-for-the-broker"></a>
### The gateway translates only to the external system only the requests that are lossless for the broker (#the-gateway-translates-only-to-the-external-system-only-the-requests-that-are-lossless-for-the-broker)

In the instant execution mode, some client trade requests with maximum price deviation specified may be unprofitable for the broker. If the operation is unprofitable for the broker, the gateway automatically generates a reply with a requote, without transmitting the trade operation to the liquidity provider. For example, if the client makes a Buy request at a price less than the price of the liquidity provider, such a request will be requoted. If a client makes a Buy request at a price greater than the price of the liquidity provider, the client's request will be executed at the price of the liquidity provider, but the client's position will be opened at the price specified by the client. The broker earns a profit from the price difference. If the client's price and the price of the liquidity provider are equal, the request is transmitted to the liquidity provider and the broker has the zero profit. The broker can increase the earned profit by correcting prices.

  * Gateway delivered together with standard installation of MetaTrader 5 platform works in trial mode, full-functional edition is purchased additionally.
  * In trial mode the gateway performs only 100 trading operations for a work session (until restart).
  * The gateway translates quotes from the external MetaTrader 5 platform. 
  * The gateway ensures that a response with one of the possible return codes will be generated for every selected request.

  
---  
  
<a id="wl"></a>
## Requirements (#wl)

For proper operation of the gateway and correct accounting of funds, it is necessary to ensure that the symbol on the broker's server have the same trading settings as the remote MetaTrader 5 platform. The symbol's trading parameters can be set in the symbols setup dialog.

In particular, it is necessary to match the following setting of symbols:

  * [Execution mode](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md) for the given symbol. If the Request or Instant Execution mode is used on a remote platform, exactly the same execution mode should be set on your server. If the Market or Exchange Execution mode is used on a remote platform, any of these two modes can be used on your side (both modes are valid).
  * For the Instant Execution mode, you should have the same [maximum order volume, above which the order is switched to the Request Execution mode (#instant)](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md#instant).
  * For the Request execution mode, the [mode of order confirmation](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md) should be enabled
  * [Contract size (#contract-size)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#contract-size)
  * [Number of digits](../../Platform-Setup/Symbols/Symbol-Settings/Common.md) after the decimal point. If the symbol price accuracy on the source server is higher than that on the receiving server, the gateway will not provide the Depth of Market for that symbol, while it will only stream tick data.
  * [The price of one point](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md) of the price change, except for instruments with the Forex calculation mode
  * [Size of one point](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md), except for instruments with the Forex calculation mode



If both platform use hedging, then the external platform must provide the ['Fill or Kill' fill policy (#fill-policy)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#fill-policy) for the symbols. It is used when forwarding pending order activations to ensure that they are executed as one order on the external server. This way, the total number of positions on the two servers will match. If the Fill or Kill policy is not available, the gateway will reject order activation requests.

Do not use the expiration mode "[Good till today including/excluding SL/TP (#gtc)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#gtc)" when forwarding orders to an external system via the gateway. This can lead to issues in the synchronization of operations, in which case "unknown execution report" errors will be printed to logs. Expired intraday orders are canceled in accordance with the [end-of-day time (#end-of-day)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#end-of-day) of the local platform, without any interaction with gateways. Even if the relevant expiration mode is enabled on a remote server, the end-of-day time may differ on that server, which will also lead to unsynchronized operation.

> The gateway does not check the matching of symbol settings, if it is used as the [liquidity provider for ECN (#price-rules)](../../Platform-Setup/ECN/Forming-Market-Depth.md#price-rules). In this case, the compatibility of trade orders with symbol settings on the remote server is provided by the ECN.

<a id="install"></a>
## Installation (#install)

MetaTrader 5 Gateway is a single executable file MetaTrader5Gateway64.exe, and it uses Gateway API. The gateway is included in the MetaTrader 5 platform, and after the installation it is located in the "gateway" subdirectory of the History Server directory.

To start working, add [the new gateway configuration](../../Platform-Setup/Gateways.md):

![Gateway Configuration](images/mt5gateway_common.png)

Set the following parameters on the "Common" tab:

  * ID â in the ID field, set the identifier of the dealer, from whose name the requests routed to the gateway will be confirmed.
  * Module â in this field, select MetaTrader5Gateway64 in the list of available modules and load its default settings.
  * Trading server â external MetaTrader 5 server IP-address and port, where trade requests are sent.
  * Trading login â login for connection to the external MetaTrader 5 server.
  * Password â password for connection to the external MetaTrader 5 server.



  * ID value must be unique in the field of manager logins and gateway identifiers. Usually, this field is filled out automatically by an acceptable default value.
  * the gateway will perform all trading operations with the liquidity provider using this trading account.

  
---  
  
Now, go to the "Parameters" tab.

![Gateway Parameters](images/mt5gateway_param.png)

The following parameters values must be specified here:

  * Max Price Deviation â the maximum allowed deviation of the current price from the price requested in an order. The order will not be executed in case that deviation has been exceeded. This parameter is used when a pending order is activated on the MetaTrader 5 side and transferred to an external system as a market order. This parameter is applied only to the symbols having "Instant" execution type.  
If a common market order is transferred to an external system, a client should specify the maximum allowable deviation. A trader cannot specify a deviation when setting pending orders. Thus, Max Price Deviation protects a trader from executing an order at considerably deviated price.
  * Limit Orders Coverage Mode â the mode of handling limit orders by the gateway. This parameter simplifies configuration of trade requests routing to the gateway, since there is no need to create a separate rule for routing the appropriate order types. Three processing modes are available:


  *     * Market â limit orders are processed on the MetaTrader 5 platform side. If an order is activated, an appropriate market order is sent to the external system.
    * Limit â limit orders are processed on the MetaTrader 5 side.  
Once a limit order is triggered, an equivalent limit order is sent to the external system. If the "Specified time" expiration type is allowed for a symbol in the external system, the expiration of 1-2 minutes is set for this limit order. Otherwise the order validity is set to the current day; in the worst case the order will be valid until canceled.  
Since the price specified in the order is already present in the market, the order will be executed with that price  a market deal will be performed. If the necessary volume of the financial instrument is not available in the market at the specified price, the order will be executed partially. In this case, a client will have a market position as well as a limit order with a residual volume, which will be further processed in a similar way on the side of MetaTrader 5.   
Limit mode allows to protect against slippage, as a limit order is sent to the the external system with a specified price rather than a market order for execution by the current price. In addition, this mode allows you not to reserve margin on a client's account before sending an order to the external system.
    * Gateway â limit orders are processed on the the external system side. Once a limit order has been placed by a client, an appropriate order is sent to the external system.
  * Symbols Path â path for importing the symbols. By default, if this parameter is absent, the gateway imports the trading symbols to \Preliminary subdirectory with trading ability disabled. A system administrator should manually allow trading for them. If this parameter is present, the gateway imports trading symbols following the specified path.
  * Symbols Update â if Yes, the gateway updates the symbol settings if they have been changed on the source server. The default is No. Settings are updated in real time. Trading sessions are updated considering the servers' time zones. Regardless of the value of "Symbols Update", the gateway does not update the following settings of symbols that exist in the platform:


  * [group and symbol background color](../../Platform-Setup/Symbols/Symbol-Settings/Common.md)
  * [quote processing and filtration parameters](../../Platform-Setup/Symbols/Symbol-Settings/Quotes.md)
  * [trading, margin calculation, execution and GTC mode](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md)
  * [spread and spread difference](../../Platform-Setup/Symbols/Symbol-Settings/Common.md)
  * [stop and freezing levels, maximum quote delay](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md)
  * [swap settings](../../Platform-Setup/Symbols/Symbol-Settings/Swaps.md)
  * [symbol time limits](../../Platform-Setup/Symbols/Symbol-Settings/Sessions.md)
  * [instant and request execution settings](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md)
  * Quotes Time Original â if "Yes", the gateway itself sets the time for ticks considering the time zone of the recipient trade server. If the parameter is absent or set to "No", the time for ticks is set by the history server according to the trade time used.
  * News Enable â if "Yes", allows transmitting news from the liquidity provider server. The default value is "No".
  * Last Price Markup â if Yes value is set, [price markup settings](../../Platform-Setup/Symbols/Symbol-Settings/Common.md) specified in an external platform (source) will be applied to streamed Last prices. Bid price spread difference values (from the Spread balance parameter) will be applied to Last prices. If you need to disable the Last price markup, set the parameter to No. The default value is Yes.  
The parameter affects Last prices only. For bid/ask prices, the gateway always applies price markup settings from an external platform.
  * Calculate Hedged Margin â when set to No (default) the gateway copies the [hedged margin (#hedged)](../../Platform-Setup/Symbols/Symbol-Settings/Margin.md#hedged) of the source symbol. If Yes, the gateway will calculate the hedged margin. If the initial margin is specified, the hedged margin is calculated as the initial margin multiplied by the Calculate Hedged Margin Rate value. If the initial margin is not specified, the hedged margin is calculated as the contract size multiplied by Calculate Hedged Margin Rate. The calculated value of the hedged margin is rounded to the number of decimal places specified in the symbol settings.
  * Calculate Hedged Margin Rate â hedged margin calculation multiplier used if Calculate Hedged Margin = Yes. Default is 2.0. 
  * Certificate Path â path to the PFX file of the certificate, which the gateway will use for [advanced authentication (#extended)](MetaTrader-5.md#extended) on an external MetaTrader 5 server.
  * Certificate Password â password to open the PFX file of the certificate used for [advanced authentication (#extended)](MetaTrader-5.md#extended).
  * Selftitled Translations â this parameter is used to prevent quotes from looping when connecting to the server on which the gateway is installed. The default value is No. For more details please see [below (#retranslation)](MetaTrader-5.md#retranslation).
  * News Category â the name of the category of news received from this data feed. Further this category name can be used to specify news to be received by separate [groups](../../Platform-Setup/Groups.md).
  * Quotes Delay â delay of transmitted quotes in seconds. The maximum duration of quotes delay is 20 minutes (1200 seconds). The flow of delayed quotes is neither thinned out, nor changed. A quote is passed to MetaTrader 5 History Server only after the expiration of delay period since the quote has arrived to Gateway API. If the temporary delay parameter is not defined, the quote delay is not used. Changes in depth of market and price statistics are delayed together with the quotes flow.
  * Quotes Tickstats Sample â the minimum frequency of sending price statistics in milliseconds. This parameter allows thinning out updates of price statistics reducing the traffic.
  * Quotes Ticks Sample â the minimum frequency of sending quotes in milliseconds. This parameter allows thinning out updates of quotes reducing the traffic. It is recommended for use on demo servers only.
  * Quotes Books Sample â the minimum frequency of depth of market updates in milliseconds. This parameter allows thinning out updates of the depth of market reducing the traffic. It is recommended for use on demo servers only.



> [Margin reservation (#margin)](MetaTrader-5.md#margin) of the clients should be configured for the appropriate order type in case Limit orders are directly transferred to the external system.

On the "Groups" tab select the group of clients, whose orders and positions will be available to the gateway.

![Setup of Groups](images/mt5gateway_groups.png)

The "Symbols" tab allows to configure the list of symbols, according to which the gateway will process trade operations and transmit the quotes.

![Setup of Symbols](images/mt5gateway_symbols.png)

MetaTrader 5 Gateway to MetaTrader 5 supports the import of symbols and their settings from an external trading server. If the option "Allow importing symbols settings" is enabled, the import of symbols from an external server will be performed. All symbols available for an account used for connection (specified in "Trading server" field of the "Common" tab) are imported. The symbols are imported to Symbols/Preliminary/ subgroup according to their hierarchy at the external server.

  * The symbols imported by the gateway are put to the "\Preliminary" symbols subgroup. All symbols have trading ability disabled. System administrator must relocate imported symbols to the proper subgroup and allow trading for them.
  * After the symbols are relocated and trading abilities are enabled, the main trading server must be restarted.
  * In case the gateway transmits configuration for the symbol that is already present in the platform, the existing symbol settings are not updated. Configuration process of such symbol is skipped.



> The gateway supports conversion of symbols and quotes. For details, please view the [Symbol and Price Translation](../../Platform-Setup/Gateways/Symbol-and-Price-Translation.md) section.

<a id="margin"></a>
## Margin Setup (#margin)

Margin reservation of the clients should be configured for the appropriate order type in case Limit orders are directly transferred to the external system.

The external system checks sufficiency of the funds that are necessary to provide any type of order placed via the gateway. However, the check is performed on the broker's general account, on behalf of which the work is carried out.

By default, the margin is charged on the side of MetaTrader 5 only when market orders are placed. When placing pending orders in an external system, the client's available funds should be controlled on the side of MetaTrader 5 before the orders are transferred to avoid using all broker's funds by the client.

After an order has been transferred to the external system, MetaTrader 5 platform is not able to check the client's margin sufficiency any more. After the order has been executed in the external system, the gateway cannot ignore that fact. Therefore, the appropriate trading operation is performed in the platform.

Set non-zero coefficients for the orders directly transferred to the external trading system in symbol settings for the appropriate symbols to configure margin collection:

![Margin Setup](images/mt5gateway_margin.png)

<a id="routing"></a>
## Configuring Trade Requests Routing (#routing)

After adding a new gateway, you must configure routing of requests so that the clients' requests are routed to this gateway. To do this add a routing rule in the "Routing - Add..." section.

In general settings, select "Process to dealers" as the action. Specify that all requests and orders must be routed according to this rule. In additional conditions, indicate groups of clients, whose requests will be passed to the gateway.

![Request Routing](images/mt5gateway_routing_common.png)

In the settings of the "Dealers" tab, add the previously created gateway.

![Request Routing](images/mt5gateway_routing_dealers.png)

After the correct execution of the steps described above, the MetaTrader 5 Gateway is started and ready to work. The result of the gateway operation is reflected in its journal. Go to the "Network" section and choose the Main Trade Server. In the appeared information dialog, in the tab "Gateways" request the logs for the corresponding period.

<a id="transferring-quotes"></a>
## Transferring quotes (#transferring-quotes)

MetaTrader 5 Gateway transfers the price flow from an external MetaTrader 5 platform.

For symbols with the [disabled market depth (#dom)](../../Platform-Setup/Symbols/Symbol-Settings/Common.md#dom) (on the external server side), the gateway passes ticks with Bid and Ask prices.

For symbols with the enabled market depth, the gateway transfers the market depth changes as well as ticks with Last prices and volumes. Ticks containing only Bid and Ask price changes are not transferred. If the best supply and demand prices change in the market depth, the history server generates the necessary tick with Bid and Ask prices and adds it to the flow.

The gateway features the built-in switching mechanism to prevent the quote flow from stopping in case the external server stops transmitting the market depth changes. If not a single market depth change for a symbol arrives from the external system within 35 seconds, the gateway stops sorting out ticks having only Bid and Ask prices. In other words, it starts transferring to the platform both Last/Volume and Bid/Ask ticks.

The following entries are shown in the gateway journal when the market depth is no longer transmitted:

2017.09.12 15:20:25.412 Gateway books stream for EURUSD stopped (no books more than 35 sec)   
2017.09.12 15:20:25.873 Gateway books stream for USDJPY stopped (no books more than 35 sec)  
---  
  
If the flow is resumed:

2017.09.12 15:21:29.759 Gateway books stream for EURUSD resumed   
2017.09.12 15:21:30.060 Gateway books stream for USDJPY resumed  
---  
  
> The gateway transmits the original stream of quotes from the external MetaTrader 5 platform, without spread markup settings specified for instruments/groups in the external platform. Only the relevant [translation settings specified on the gateway](MetaTrader-5.md) are applied to the prices.

<a id="markup"></a>
## Price Markups (#markup)

The gateway receives prices from the MetaTrader 5 external server and transmits them to clients taking into account transformation settings (markups). The clients perform trade operations using transformed prices. However, while processing trading operations on the gateway and their transmission to the external system, initial, not transformed prices are automatically used.

Thus, a brokerage company receives its profit share from each deal performed at the external system.

Markup values are set separately for Bid and Ask prices by each symbol:

![Configuring transformations](images/mt5gateway_translations.png)

In this example, the following corrections are specified for EURUSD: for each tick the Bid price will be reduced by 3 points, and the Ask price will be increased by 3 points. 

If no correction is set for a symbol, the clients will work with the original prices of the liquidity provider.

<a id="retranslation"></a>
### Symbol masks and own price retranslation (#retranslation)

In translation settings, "*" mask can be used as the source symbol and as the destination symbol in the platform. For example, the settings Symbol="*", Source="*" mean that the names of the symbols will be used as they are provided in the external system. If the symbol is entitled EURUSD in the external system, then its data will be feed to the symbol with the same name on the trading platform side. The only situation in which such settings cannot be used is the connection of the gateway to the platform on which it is installed. In this case, receiving and feeding of quotes by the gateway into the same symbols will lead to looping.

To avoid such situations, the gateway provides the parameter "[Selftitled Translations (#selftitled-translations)](MetaTrader-5.md#selftitled-translations)". If it is set to "No" (default) and the gateway has a translation setting "*" <\- "*", the gateway will not start. An appropriate entry will be added into the journal:

translation rule for symbols to themselves '* <\- *' not allowed but exists, remove this rule or allow it by 'Selftitled Translations' parameter  
---  
  
Before enabling this parameter, make sure that the gateway is not connected to the same cluster on which it is running. Otherwise, this can lead to the looping of transactions, configurations and quotes in the platform.

<a id="example-of-metatrader-5-gateway"></a>
## Example of MetaTrader 5 Gateway (#example-of-metatrader-5-gateway)

All trade operations performed by the gateway are included in the gateway journal. For example, using the client terminal we buy EURUSD 1.0. After processing the request, the following entries will appear in the journal of the MetaTrader 5 Gateway:

'1002': request #1179132 received (#2073 instant buy 1.00 EURUSD at 1.31237)  
'1002': request #1179132 answered - Done at 1.312370 (#1002 instant buy 1.00 EURUSD at 1.31237)(based on #2448959, #2448959, 1.31198 / 1.31212)  
---  
  
Consider the contents of the logs in more detail.

A request with the ID # 1179132 is received from the broker's client with the account 1002. Corresponding to this request, on the broker's server there is the client's order with the ID # 2073 to Buy one lot of EURUSD at the price of 1.31237.

To the request ID #1179132, the broker's client with the account 1002 receives a reply that the request has been executed (Done), with the request execution price - 1.312370. In addition the original order of the client is specified. The last part of the message contains the parameters of the trading operation on the remote platform. In particular, upon the client's request, generated order # 2448959, deal # 2448959, with the actual execution prices: Sell - 1.31198, Buy - 1.31212. In this case, this means that the client's Buy has been executed at 1.31212 on the external trading platform.

On this basis we can calculate the profit from the price difference:

The broker's profit = 1.31237 - 1.31212 = 0.00025.

<a id="extended"></a>
## Operation in the advanced authentication mode (#extended)

The [advanced authentication (#authorization)](../../Platform-Setup/Groups/Group-Settings.md#authorization) mode can be enabled for the account used by the gateway for connection to an external MetaTrader 5 server. In this case, the PFX certificate file is required for connection, in addition to the login and password. The file path and a password for file opening must be specified in appropriate gateway parameters: [Certificate Path (#certificate)](MetaTrader-5.md#certificate) and [Certificate Password (#certificate)](MetaTrader-5.md#certificate).

To receive the certificate, please contact the broker or generate a certificate using the client terminal. In the latter case, connect to the account and go through the [standard generation procedure (#generation)](https://www.metatrader5.com/en/terminal/help/start_advanced/extended_authorization#generation). The resulting PFX file should be transferred to the computer, on which the gateway is running. Save it to a disk or install it in Windows storage. When installed to the storage, the 'Certificate Path' parameter can be left empty; thus the gateway will request the certificate from the storage.

> When installing the certificate to the Windows storage, make sure to select the Local Computer storage, and not that of the Current User. Otherwise the gateway will not be able to access the certificate.

If the advanced authentication is required, but the gateway cannot find the certificate at the path specified in 'Certificate Path', the following error will be added in its log:

'2098': loading of standard SSL certificate from 'C:\\{path}\2098_ServerName.pfx1' failed  
---  
  
If the certificate cannot be found in the Windows storage, the following error will be added:

'2098': standard SSL certificate for advanced authorization is not found  
---  
  
If an invalid password is specified in 'Certificate Password', the following error will be written in the log:

'2098': invalid standard SSL certificate password  
---  
  
<a id="coverage"></a>
## Coverage using MetaTrader 5 Gateway to MetaTrader 5 (#coverage)

The MetaTrader 5 trade platform allows covering the positions of clients on other trade servers protecting own company from financial risk. Coverage of positions can be performed using the MetaTrader 5 Gateway to MetaTrader 5.

Coverage of client positions is performed using special coverage accounts. Such accounts are those created in [groups](../../Platform-Setup/Groups.md) whose names start with symbols "coverage" (case sensitive). For example, coverage\forex. Performing trade operations on a coverage account, a manager covers the position of clients on another trade server.

In order to make covering possible, an administrator of the trade platform should make the corresponding settings:

<a id="creating-a-group"></a>
### Creating a Group (#creating-a-group)

[Create a group (#name)](../../Platform-Setup/Groups/Group-Settings.md#name), whose name starts with "coverage":

![Group of accounts for hedging](images/coverage_group.png)

<a id="creating-a-coverage-account"></a>
### Creating a Coverage Account (#creating-a-coverage-account)

In the coverage group, [create an account](../../Platform-Setup/Accounts/Creating-Account.md). This account will be used by a manager for performing trade operations that cover client positions.

![Hedge account](images/coverage_account.png)

<a id="opening-a-trade-account"></a>
### Opening a Trade Account (#opening-a-trade-account)

You need to open a trade account on an external trade server, where coverage positions will be opened. The account should have enough deposit for covering client positions.

<a id="setting-up-the-gateway"></a>
### Setting up the Gateway (#setting-up-the-gateway)

The next step is [setting up](../../Platform-Setup/Gateways/Configuration-of.md) the MetaTrader 5 Gateway using the authorization details of the account opened at the external trade server. Then you need to set up the [routing of trade operations](../../Platform-Setup/Routing.md) from the coverage account to the external trade system through the gateway:

![Setting up the routing](images/coverage_routing.png)

After that, specify the MetaTrader 5 Gateway to MetaTrader 5 in the Dealers tab.

Once the coverage account is set up, a manager can perform trade operations using it in the manager terminal. The summary rates for all coverage accounts on the trade server are displayed in the Summary positions and Exposure tabs of the Toolbox window in the manager terminal.

```

---

<a id='history-server-console-commands-md'></a>
### 119. `History-Server/Console-Commands.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [History Server](../History-Server.md) / Console Commands

[Previous](Quotes-Filtration.md) | [Next](../Backup-Server.md)

# Console Commands

The history server component [mt5srvupdater64.exe](Structure-of-Directories-and-Files.md) has several console commands that allow updating and activating the platform if servers are unavailable for connection via the administrator terminal.

In order to execute these commands, start file mt5srvupdater64.exe from the root directory of the history server, specifying corresponding keys:

  * /update — download updated files of all the system components, if there are such files, from the developer's update server;
  * /upgrade — install [updates](../../Platform-Setup/Live-Update.md) of all the platform components. This command can be executed only of the updates have been downloaded;
  * /activate — [activate](../../Platform-Installation/Activation.md) the platform.



For example, after you execute command "mt5srvupdater64.exe /update /upgrade", the platform updates will be downloaded and installed.

> The protocol of the update process is kept in , located in folder .

```

---

<a id='history-server-interaction-with-quote-providers-md'></a>
### 119. `History-Server/Interaction-with-Quote-Providers.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [History Server](../History-Server.md) / Interaction with Quote Providers

[Previous](Structure-of-Directories-and-Files.md) | [Next](Quotes-Filtration.md)

# Interaction with Quote Providers

In MetaTrader 5, [gateways](../../Platform-Setup/Gateways.md) and [data feeds](../../Platform-Setup/Data-Feeds.md) can be used as providers of quotes. Their interaction with the history server is identical. This interaction can be analyzed in terms of the physical connection and at the level of quotes streaming.

## Physical Connection

The physical connection must be established for each source of quotes enabled in the appropriate settings of the platform. The physical connection details can be configured on the "Timeouts" tab of [gateways (#timeouts)](../../Platform-Setup/Gateways/Configuration-of.md#timeouts) and [data feeds (#timeouts)](../../Platform-Setup/Data-Feeds/Configuration-of.md#timeouts). Let's consider the following configuration example:

  * Interval between reconnections = 5 seconds.
  * Number of reconnection attempts = 10.
  * Interval between series of reconnections = 60 seconds.



If a gateway/data feed loses connection with an external server, a reconnection attempt is made in 5 seconds. If it fails, another one is made in 5 seconds. The total number of attempts is 10. If unable to reconnect, a series of attempts is repeated after a pause of 60 seconds.

## Stream of Quotes

A stream of prices for several symbols goes through each physical connection to a quote provider.

At each point of time, the history server accepts the stream of prices for a certain symbol only from one quote provider, while other price streams of the same symbol are ignored. The source selected for the stream of prices for a symbol is considered a current (active) source for this symbol.

During operation the active source for an instrument may change. It is changed in accordance with [priority (#switching)](../../Platform-Setup/Data-Feeds.md#switching) settings. The priority of data feeds and gateways is determined by their position in the list.

> The priority of [gateways](../../Platform-Setup/Gateways.md), if they are used as a source of quotes, is always higher than that of data feeds.

The stream of prices switches to the source with a [higher priority (#switching)](../../Platform-Setup/Data-Feeds.md#switching) as soon as the first quotes for a symbol is received from that source.

It switches to the source with a lower priority by a timeout. In case no quotes are received from the active quote source during a certain time period (it is specified in the "Datafeeds timeout" parameter in [history server settings (#timeout)](../../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md#timeout)), then the history server switches to a source with the lower priority that provides quotes for the same symbol.

> The time to wait for a quote for a symbol is defined in the "Datafeeds timeout" parameter in [history server settings (#timeout)](../../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md#timeout).

After a new quotes source is selected, it is considered active. All cases of server switching to streams from other sources are reflected in the [journal](../../Platform-Setup/Network-cluster/Journal.md) in the form of the following entry:

2011.03.10 10:11:05 Ticks datafeed 4: CHFJPY activation  
---  
  
Here the entry means that for CHFJPY, a stream of quotes from the fourth data feed (a position in the list of data feeds at the moment the entry is made) is selected.

```

---

<a id='history-server-quotes-filtration-md'></a>
### 119. `History-Server/Quotes-Filtration.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [History Server](../History-Server.md) / Quotes Filtration

[Previous](Interaction-with-Quote-Providers.md) | [Next](Console-Commands.md)

# Quotes Filtration

The filtration system is intended for controlling the correctness of quotes on financial symbols from [data feeds](../../Platform-Setup/Data-Feeds.md). Filters can be set upon the ["Quotes"](../../Platform-Setup/Symbols/Symbol-Settings/Quotes.md) tab of each symbol.

  * Filters cannot be applied to instruments with the [enabled Depth of Market (#dom)](../../Platform-Setup/Symbols/Symbol-Settings/Common.md#dom) and with the one of the following properties: [Exchange calculation type (#calculation)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#calculation) (begins with "Exchange") or [Last price based charting mode (#charts)](../../Platform-Setup/Symbols/Symbol-Settings/Common.md#charts). Also, filtering is not applied to [splice symbols](../../Platform-Setup/Symbols/Splicing-Futures.md).


  * To completely disable filtering, set 0 for all levels: Soft, Hard and Discard.


  * The platform automatically filters out negative and zero Bid and Ask prices of OTC instruments, regardless of whether their Market Depth is enabled or not. OTC (over-the-counter or off-exchange) symbols include financial instruments whose [calculation type (#calculation)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#calculation) does not start with "Exchange".


  * Analysis and filtration are performed separately for Bid and Ask.


  * Filters are not applied to the first tick after a break in the quotes stream: after platform restart, after a break in [quoting sessions](../../Platform-Setup/Symbols/Symbol-Settings/Sessions.md), after [off-hours](../../Platform-Setup/Time.md) and after [holidays](../../Platform-Setup/Holidays.md). Filtration cannot be applied because it is not known in advance what was the price preceding the break. This rule does not apply to other price checks, including [allowable spread (#spread)](../../Platform-Setup/Symbols/Symbol-Settings/Quotes.md#spread).

  
---  
  
Three levels of quote filtration are available:

  * Soft filtration — the soft filtration level is the first border of the channel of allowed symbol prices. If a new price (Bid or Ask) differs from the previous one by more than the specified value (in points), it is deleted from the thread translated to clients. However, if such a price difference appears again the number of times specified in the "Filter" field, the new price level is accepted, and the filtration level is shifted by the specified value. Such quotes will be translated again.
  * Hard filtration — the hard filtration level is the second border of the price channel. If a received quote exceeds the level both of the soft and of the hard filtration, it is cut out from the thread translated to clients. For a new level of accepted price to be set, the quotes must be repeat the number of times specified in both levels;
  * Discard filtration level — if the difference between prices of the previous and new quote exceed the specified value, such new prices are definitely removed from the thread.



![Operation scheme of filters](images/filtration_scheme.png)

![Channel of allowed prices](images/filtration_scheme_acceptable.png) | — channel of allowed prices | ![Previous quote](images/filtration_scheme_previous.png) | — previous quote  
---|---|---|---  
![Soft filtration zone](images/filtration_scheme_soft.png) | — soft filtration zone | ![New quote](images/filtration_scheme_next.png) | — new quote  
![Hard filtration zone](images/filtration_scheme_hard.png) | — hard filtration zone | N | — number of quotes (set in the "Filter" filed) required to move to a new level  
![Discard filtration zone](images/filtration_scheme_discard.png) | — discard filtration zone |   
  
It is considered that there is a certain acceptable channel of price data fluctuation. This channel is limited by the set level of soft filtration. If the Bid or Ask price of the newly received quote differs from appropriate prices of the previous quote by the value of the specified soft filtration level, it is discarded. If several following quotes (the number is specified in the "Filter" parameter) also exceed the soft filtration level, the new price channel is set.

Example:  
---  
The last EURUSD quote was 1.50213/1.50231 (Bid/Ask). The soft filtration level is equal to 150, "Filter" parameter is equal to 3. The following quotes are received: 1.50373/1.50391, 1.50370/1.50388, 1.50372/1.50390, 1.50374/1.50392. In this case the first three quotes will be filtered away, because they exceed the previous one by more than 150 points. The last quote will be let in, and the new filtration level will be set 1.50374/1.50392 ± 150.   
  
The hard filtration level is an additional way to protect from incorrect quotes. If a new quote differs from the previous one by the value that is higher than the specified hard filtration level, it will be filtered away. The additional hard filtration protection is a more complicated mechanism of setting the new price channel. To confirm the new level, first the soft filter (specified number of quotes that exceed this value) must be passed, and then the hard one.

The discard filtration implies the unconditional filtering away of quotes that differ by this value. Such prices are deliberately considered incorrect.

## Filtration of Similar Quotes

The trading platform filters similar quotes received from data sources. If the platform receives the same quote as the previous one within a minute, it skips the quote. If the time interval is greater than one minute, the platform accepts the quote. The same quote is also accepted if the minute has changed. It allows plotting the charts correctly on a low liquidity market.

Example:

  * 13:01:15 a quote is received
  * 13:01:32 the same quote is received, it is not accepted
  * 13:01:50 the same quote is received, it is not accepted
  * 13:02:01 the same quote is received, it is accepted (the interval between quotes is less than 60 seconds, but the minute has changed)



## Spread Control

The Minimum Spread and Maximum Spread parameters in the Quotes tab are provided for additional protection. If the difference between the Bid and Ask prices in the incoming quote does not fall within the specified values, such a quote is removed from the stream.

The check only applies to over-the-counter (OTC) financial instruments with the [floating spread (#spread)](../../Platform-Setup/Symbols/Symbol-Settings/Common.md#spread). OTC instruments have one of the following [calculation types (#calculation)](../../Platform-Setup/Symbols/Symbol-Settings/Trade.md#calculation): Forex, Futures, CFD, CFD Leverage or CFD Index.

```

---

<a id='history-server-structure-of-directories-and-files-md'></a>
### 119. `History-Server/Structure-of-Directories-and-Files.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [History Server](../History-Server.md) / Structure of Directories and Files

[Previous](../History-Server.md) | [Next](Interaction-with-Quote-Providers.md)

# Structure of Directories and Files

The history server is installed to folder "history_server". It contains the following executable files:

  * mt5srvupdater64.exe — the executable file of the live update system of the history server. This component has a number of [console commands](Console-Commands.md);
  * mt5history64.exe — the executable file of the history server.



The main directory of the history server contains the following folders: bases, config, datafeed, gateway, history, liveupdate, logs, plugins.

The bases directory contains different data bases:

Files and folders | Description | Files and folders | Description  
---|---|---|---  
ecn\ | [ECN](../../Platform-Setup/ECN.md) data directory. | executions\ | Bases and indexes of ECN trade executions by trade servers.  
history\ | Bases and indexes related to the history of client order execution in ECN, by months.  
symbols\\{Symbol}\matching.dat | Symbol databases related to client orders placed in ECN for matching.  
symbols\\{Symbol}\filling_items.dat | Symbol databases of matching operations processed in ECN.  
symbols\\{Symbol}\books\yyyymmdd.book | ECN Market Depth journals by days.  
filling_orders.dat | Databases of internal ECN order which are executed on gateways.  
performance\ | Monthly history server performance databases and data indexes, which are displayed on the [Monitoring](../../Platform-Setup/Network-cluster/Monitor.md) tab.  
news.dat | News data base.  
news.idx | The index file of the news database.  
  
The config directory contains different configurations as *.ini files:

Files | Description  
---|---  
common.ini | Common History Server settings.  
ecn_symbols.ini | [ECN](../../Platform-Setup/ECN.md) symbol settings.  
mt5srvupdater.ini | [Update](../../Platform-Setup/Live-Update.md) settings.  
history_sync.ini | Settings of [history data synchronization](../../Platform-Setup/Synchronization.md).  
server.ini | Individual settings of the access server.  
servers.ini | Settings of the internal [network of servers](../../Platform-Setup/Network-cluster.md).  
symbol_groups.ini | Individual settings of [symbols for groups](../../Platform-Setup/Groups/Group-Symbol-Settings.md).  
symbols.ini | [Symbol](../../Platform-Setup/Symbols.md) settings.  
time.ini | [Time](../../Platform-Setup/Time.md) settings.  
  
The datafeed directory contains files for working with [data feeds](../../Platform-Setup/Data-Feeds.md):

Files | Description  
---|---  
[datafeed_name]\logs\yyyymmdd.log | Journal files in which records regarding data feed operation are stored. For each data feed which has been added through the [relevant section](../../Platform-Setup/Data-Feeds.md) of the Administrator terminal, a separate journal file is created. The file name is set in accordance with the data feed name.  
[datafeed_name]\*.dat | Data files with data feed settings.  
*.exe | Data feed executables. It is not allowed to have several datafeed executable files with the same name in the history server directory. If you place several identical files in different subdirectories, this may lead to conflicts in the operation and display of modules in the Administrator terminal.  
MT5APIGateway.dll, MT5APIGateway64.dll | Libraries for data feed operation.  
  
The gateway directory contains files for working with [gateways](../../Platform-Setup/Gateways.md):

Files and folders | Description  
---|---  
[gateway_name]\\[gateway configuration name]\logs\yyyymmdd.log | Journal files in which gateway operation logs are stored. For each data feed which has been added through the [relevant section](../../Platform-Setup/Gateways.md) of the Administrator terminal, a separate journal file is created. The file name is set in accordance with the data feed name.  
[gateway_name]\\[gateway configuration name]\*.dat | Data files with gateway settings.  
*.exe | Gateway executables. It is not allowed to have several datafeed executable files with the same name in the history server directory. If you place several identical files in different subdirectories, this may lead to conflicts in the operation and display of modules in the Administrator terminal.  
MT5APIGateway.dll, MT5APIGateway64.dll | Libraries for gateway operation.  
  
The history folder contains [history data](../../Platform-Setup/1-Minute-History-Charts.md) divided by symbols:

Folders | Files | Description  
[2 chars]\\[symbol]\ | yyyy.hsc | History data on a symbol, divided by years. '2 chars' are the first two characters in the instrument name; 'symbol' is the name of the instrument. Arranging symbol data in different directories reduces the load on the file system and provides faster data operations.  
[2 chars]\\[symbol]\ | yyyy.tkc | Tick data on a symbol, divided by years. '2 chars' are the first two characters in the instrument name; 'symbol' is the name of the instrument. Arranging symbol data in different directories reduces the load on the file system and provides faster data operations.  
  
The liveupdate folder contains the latest updates of all the platform components:

Files | Description  
---|---  
mt5adm.build | Live update of the administrator terminal. The build number is specified after the point.  
mt5as.build | Live update of the access server.  
mt5bs.build | Live update of the backup server.  
mt5clw.build | Live update of the client server.  
mt5clwide.build | Live Update of MetaEditor.  
mt5clwmql.build | Live Update of the MQL5 compiler.  
mt5hs.build | Live update of the history server.  
mt5hsu.build | Live update of the update system of the history server.  
mt5man.build | Live update of the manager server.  
mt5ts.build | Live update of the trade server.  
  
The logs folder contains log files of the history server operation, as well as crash logs:

Files and folders | Description  
---|---  
Crash\crash.log.* | The /crash directory contains server crash files. These files are automatically sent to the software developing company for detecting reasons of the crash and eliminating them.  
yyyymmdd.log | [Journal](../../Platform-Setup/Network-cluster/Journal.md) files that contain all the information about events that occur on the history server. Server logs are stored in separate files for each working day. Here yyyy — year, mm — month, dd — day.   
mt5srvupdater.log | Journal files of the platform [updates](../../Platform-Setup/Live-Update.md).

```

---

<a id='trade-server-daily-reports-md'></a>
### 119. `Trade-Server/Daily-Reports.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Trade Server](../Trade-Server.md) / Daily Reports

[Previous](Mail-Templates.md) | [Next](SendMail-Utility.md)

# Daily Reports

At [the end of each working day and month, (#end-of-day)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#end-of-day) the trade server prepares reports on client deals and places them to [trade server directory]/confirms/YYYYMMDD", where YYYYMMDD is the current date). Each report is an HTML file having the name "login_mail.htm" (for example, "123_mail.htm"). After creating the reports, the trade server sends them using [SendMail](SendMail-Utility.md) utility.

The database of all generated reports is saved in the file [trade server directory]/bases/daily.dat. The data from the database can be requested via the Manager terminal, for example, by using a report from [Daily Report](../../Platform-Setup/Reports/Daily.md) standard delivery.

## Enabling/Disabling Daily Reports

Generation of reports can be enabled/disabled for each [client group (#reports)](../../Platform-Setup/Groups/Group-Settings.md#reports) separately.

![Reports](images/groups_reports.png)

Here you can also configure sending reports to clients and (if necessary) the technical support via email.

## Customizing Report Appearance

Email templates with [daily (#daily)](Mail-Templates.md#daily) and [monthly (#monthly)](Mail-Templates.md#monthly) trading activity reports are located in the /templates/confirmation and /templates/statement folders of the trade server. 

## Configuring Daily Report Generation Time

Daily and monthly report generation time is defined [by the trade server settings (#end-of-day)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#end-of-day): 

![End of day](images/network_add_eod.png)

The reports are affected by the following parameters:

  * End of day time — report generation start time.
  * End of day schedule — report generation days. The option does not affect monthly reports.
  * Daily statements — daily report generation time: at the end of a trading day (before charging swaps, annual interest, and commissions) or at the start of a trading day (after charging swaps, annual interest, and commissions).
  * Monthly statements — monthly report generation time: at the end of the last day of month (before charging swaps, annual interest, and commissions) or at the start of a first day of the next month (after charging swaps, annual interest, and commissions).



## Report Data

Name | Description  
---|---  
Datetime | Daily report generation date and time.  
Login | Initial key. The login of a client for whom the daily report is generated.  
DatetimePrev | Daily report previous generation date and time.  
Name | The name of a client in a daily report.  
Group | Client group in a daily report.  
Currency | Client's deposit currency in a daily report.  
Company | The company serving the client in a daily report.  
EMail | An email of a client in a daily report.  
Balance | The size of a client's balance in a daily report.  
Credit | The amount of a client's credit funds in a daily report.  
InterestRate | The annual interest rate of a client in a daily report.  
CommissionDaily | The amount of commissions charged from a client for a day in the report.  
CommissionMonthly | The amount of commissions charged from a client for the current month in a report.  
AgentDaily | The size of agent commissions charged for a client's trade operations for a day, from a daily report.  
AgentMonthly | The amount of agent commissions charged for a client's trade operations for the current month.  
BalancePrevDay | Client's balance as of the end of the previous day.  
BalancePrevMonth | Client's balance as of the end of the previous trading month.  
EquityPrevDay | A client's equity as of the end of the previous day.  
EquityPrevMonth | The value of a client's equity as of the end of the previous trading month.  
Margin | Size of a client's margin in a daily report. The report does not contain data on the margin charged for each position or order because in some cases, it is not possible to calculate the margin value for the following reasons:

  * On hedging accounts, multiple oppositely directed positions can exist for the same instrument. If their volumes do not match, the [hedged margin](../../Platform-Setup/Symbols/Symbol-Settings/Trade/Margin-Calculation/Retail-Forex-CFD-Futures-—-Hedging.md) is calculated based on the aggregate positions.
  * If on a netting account the margin is charged for pending orders and there are two oppositely directed orders for the same instrument, it is unknown in which of them the margin should be indicated. It is not known in advance which of the orders will be used to open a position and which one to close it.
  * When using [spreads](../../Platform-Setup/Spreads.md), the margin depends on the aggregate orders and positions.

  
MarginFree | A client's free margin in a daily report.  
MarginLevel | The margin level of a client in the daily report.  
MarginLeverage | The margin leverage of a client in the daily report.  
Profit | The size of the current profit for all open positions of a client in a daily report.  
ProfitStorage | The current size of swaps charged for a client's open positions for a day, but not yet reflected in the balance.  
ProfitEquity | The amount of the current floating equity of a client in a daily report.  
DailyProfit | The amount of a client's daily profit.  
DailyBalance | The amount accrued to a client's balance during the reported day.  
DailyCredit | The amount of credit given to a client during the reported day.  
DailyCharge | The amount of other charges to the client's balance during the reported day.  
DailyCorrection | The amount of corrective balance operations for a reported day.  
DailyBonus | The amount of bonuses added to the client's balance for the reported day.  
DailyStorage | The amount of swaps calculated for the client for the reported day.  
DailyCommInstant | The amount of instant commissions charged from the client for a reported day.  
DailyCommRound | The amount of turnover commissions charged from the client for a reported day.  
DailyCommFee | The fee amount charged for the client's deals for the reported day.  
DailyAgent | The size of agent commissions charged for a client's trade operations for the reported day.  
DailyInterest | The amount accrued to a client as part of the annual interest rate for the reported day.

```

---

<a id='trade-server-mail-templates-md'></a>
### 119. `Trade-Server/Mail-Templates.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Trade Server](../Trade-Server.md) / Mail Templates

[Previous](Structure-of-Directories-and-Files.md) | [Next](Daily-Reports.md)

<a id="mail-templates"></a>
# Mail Templates (#mail-templates)

Several types of emails that are automatically sent to clients are implemented in the the MetaTrader 5 platform:

  * Welcoming email at account opening;
  * Email requesting the certificate confirmation;
  * Daily report on trade activity;
  * Monthly report on trade activity.



  * All templates must be of the Unicode format (UTF-16/UCS-2 Little Endian). 


  * In order to start using a new template, the main trade server must be restarted.

  
---  
  
<a id="greeting"></a>
## Welcoming Emails (#greeting)

Welcome messages are sent to clients through the internal mail system when an account is opened. It does not matter how the account is opened: by the trader via the client terminal or by the broker via the Manager/Administrator terminal. The welcome email contains the account number and password, as well as general information about the MetaTrader 5 platform.

Welcome email templates are located in the following [directory (#templates)](Structure-of-Directories-and-Files.md#templates):

  * Trader server directory\templates\greeting\default\*.htm — default templates used for groups;
  * Trader server directory\templates\greeting\custom folder*.htm — templates of emails that can be sent only to separate groups with account of their settings;
  * Trader server directory\templates\greeting\preliminary\*.htm — templates of emails that are sent when a [preliminary account (#preliminary)](../../Platform-Setup/Groups/Group-Types.md#preliminary) is opened from the client terminal.



> An unlimited number of folders with special templates can be create. The name of the folder with templates that will be used for a group are specified in the "Company" tab in its [settings (#templates-folder)](../../Platform-Setup/Groups/Group-Settings.md#templates-folder).

<a id="certificate"></a>
## Certificate Confirmation Email (#certificate)

These letters are sent if the [extended authorization (#authorization)](../../Platform-Setup/Groups/Group-Settings.md#authorization) and [certificate confirmation (#confirm)](../../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server/Extended-Authorization.md#confirm) mode is enabled for this group. Such an email contains information on how to confirm a certificate. Templates of such emails are stored in the following [directory (#templates)](Structure-of-Directories-and-Files.md#templates):

  * Trader server directory\templates\certificate\default\*.htm — default templates used for groups;
  * Trader server directory\templates\certificate\custom folder*.htm — templates of emails that are sent only to separate groups with account of their settings.



<a id="confirm"></a>
## Phone and Email Verification (#confirm)

These emails\messages are sent to [verify phone numbers and emails (#confirmation)](../../Platform-Setup/Accounts/Account-Allocation-Settings.md#confirmation), specified during registration of demo and preliminary accounts from client terminals.

  * Trader server directory\templates\verify_email\default\*.htm — email templates as HTM files.
  * Trader server directory\templates\verify_phone\default\*.htm — SMS templates as text files. Do not use too long messages. If the allowed length is exceeded (depending on the provider), a message may be cropped or split into multiple SMS.



The <!--CONFIRMATION_CODE--> macro is used for confirmation emails. This code adds the generated confirmation code to the text.

Templates from the "default" folder are used on default for all groups. If you need to use custom templates for a specific group, create another folder in the same directory and place the template files to it. Then specify the folder name in the [group settings (#templates-folder)](../../Platform-Setup/Groups/Group-Settings.md#templates-folder).

<a id="daily"></a>
## Daily Report on Trade Activity (#daily)

Daily reports on trade activity of clients are sent if the "Send daily statements by email" option is enabled in the [group settings (#reports)](../../Platform-Setup/Groups/Group-Settings.md#reports). Templates of such emails are stored in the following:

  * Trader server directory\templates\confirmation\default\*.htm — default templates used for groups;
  * Trader server directory\templates\confirmation\custom folder*.htm — templates of reports that are sent only to separate groups with account of their settings.



<a id="monthly"></a>
## Monthly Report on Trade Activity (#monthly)

Monthly reports on trade activity of clients are sent if the "Send daily statements by email" option is enabled in the [group settings (#reports)](../../Platform-Setup/Groups/Group-Settings.md#reports). Templates of such emails are stored in the following:

  * Trader server directory\templates\statement\default\*.htm — default templates used for groups;
  * Trader server directory\templates\statement\custom folder*.htm — templates of reports that are sent only to separate groups with account of their settings.



<a id="multilanguage"></a>
## Email templates in different languages (#multilanguage)

All template files should be named according to the language they are written in. A file name is used by the platform to determine which users the template is to be applied to. The user's language is defined in the [account settings (#personal)](../../Platform-Setup/Accounts/Editing-Account.md#personal).

Languages are specified in the format standard for the family of Windows operating systems, though without the specification of regional dialect specifics. E.g. English.htm, Russian.htm and so on. The only exceptions are Chinese language templates. In case of simplified Chinese, a template should be named chinese.htm, while in case of traditional Chinese, it is named chinese_traditional.htm.

If no template was found for the language specified in the account, the default.htm template is used. If a separate folder is specified for a group, the default template is first searched for in this folder, and if it is not found an email according to the default.htm template located in the "Default" folder is sent.

<a id="the-format-of-files"></a>
## The Format of Files (#the-format-of-files)

A template file can contain a plain text, HTML tags, as well as CSS design elements. To insert images, set them on your web server and specify the appropriate links in <img src="URL">. The web server must operate using the HTTPS protocol. Images with URLs starting with http:// will not be displayed.

Besides, the templates can be equipped with special macros for inserting various data depending on an account an email is sent to.

  * Common macros
  * <!--ACCOUNT--> — account number.
  * <!--LOGIN--> — account number.
  * <!--GROUP--> — user group.
  * <!--PASSWORD--> — account master password.
  * <!--INVESTOR--> — account investor password.
  * <!--NAME--> — user first name (obsolete macro).
  * <!--USERNAME--> — user first name (obsolete macro).
  * <!--FIRST_NAME--> — user first name.
  * <!--LAST_NAME--> — user last name.
  * <!--MIDDLE_NAME--> — user middle name.
  * <!--COUNTRY--> — country of residence.
  * <!--CITY--> — city of residence.
  * <!--STATE--> — state (region) of residence.
  * <!--ZIPCODE--> — zip code.
  * <!--ADDRESS--> — residential address.
  * <!--PHONE--> — phone number.
  * <!--EMAIL--> — email address.
  * <!--COMMENT--> — account comment.
  * <!--ID--> — ID.
  * <!--STATUS--> — residency status.
  * <!--PHONEPASS--> — phone password.
  * <!--AGENT--> — agent account associated with the user.
  * <!--CURRENCY--> — account deposit currency.
  * <!--COMPANY--> — [company name (#company-name)](../../Platform-Setup/Groups/Group-Settings.md#company-name) from the account group settings.
  * <!--LEVERAGE--> — recipient's current leverage.



<a id="daily-and-monthly-report-macros"></a>
### Daily and monthly report macros (#daily-and-monthly-report-macros)

  * <!--DATE--> — date the report is generated for, YYYY.MM.DD.
  * <!--TIME--> — time the report is generated for, HH::MM:SS.
  * <!--FULLTIME--> — date and time the report is generated for, YYYY.MM.DD HH::MM:SS.
  * <!--BALANCE--> — balance at the time of the report generation.
  * <!--CREDIT--> — credit funds at the time of the report generation.
  * <!--INTERESTRATE--> — client's annual interest rate.
  * <!--COMMISSION_DAILY--> — amount of standard commissions charged from a client for the day the report is generated for.
  * <!--COMMISSION_MONTHLY--> — amount of standard commissions charged from a client for the month the monthly report is generated for (or for the current month in case of a daily report).
  * <!--AGENT_DAILY--> — agent commissions charged from a client for the day the report is generated for.
  * <!--AGENT_MONTHLY--> — agent commissions charged from client's operations for the month the monthly report is generated for (or for the current month in case of a daily report).
  * <!--PREV_BALANCE_DAILY--> — client balance at the end of the previous trading day.
  * <!--PREV_BALANCE_MONTHLY--> — client balance at the end of the previous month.
  * <!--PREV_EQUITY_DAILY--> — client equity at the end of the previous trading day.
  * <!--PREV_EQUITY_MONTHLY--> — client equity at the end of the previous month.
  * <!--PREV_DATE--> — the date of the last but one closure of the trading day.
  * <!--PREV_TIME--> — the time of the last but one closure of the trading day.
  * <!--PREV_FULLTIME--> — the date and time of the last but one closure of the trading day.
  * <!--MARGIN--> — money required to cover open positions as of the end of the day/month.
  * <!--MARGIN_FREE--> — amount of free margin volume as of the end of the day/month.
  * <!--MARGIN_LEVEL--> — margin level as of the end of the day/month.
  * <!--FLOATING_PROFIT--> — floating profit/loss on all open positions at the time of the report generation.
  * <!--FLOATING_STORAGE--> — size of swaps charged for client's positions for a day, but not yet reflected in the balance.
  * <!--FLOATING_COMMISSION--> — floating client commission blocked on the account but not yet reflected in the balance at the time of the report generation.
  * <!--FLOATING_EQUITY--> — client equity volume at the time of the report generation.
  * <!--FLOATING_PL--> — total client's floating profit/loss at the time of the report generation. Calculated as <!--FLOATING_PROFIT--> \+ <!--FLOATING_STORAGE--> \+ <!--FLOATING_COMMISSION-->.
  * <!--FLOATING_LIABILITIES--> — amount of client liabilities at the time of report generation. It is only used for the [Exchange risk management model (#risk)](../../Platform-Setup/Groups/Group-Settings.md#risk).
  * <!--FLOATING_ASSETS--> — amount of client assets at the time of report generation. It is only used for the [Exchange risk management model (#risk)](../../Platform-Setup/Groups/Group-Settings.md#risk).
  * <!--CLOSED_PROFIT--> — total closed profit/loss at all deals per day/month.
  * <!--CLOSED_STORAGE--> — size of swaps charged for a client's positions for a day/month.
  * <!--CLOSED_DEPOSIT--> — total funds deposited/withdrawn from the account per day/month.
  * <!--CLOSED_CREDIT--> — credit funds deposited/withdrawn from the account per day/month.
  * <!--CLOSED_CHARGE--> — other depositions/withdrawals from the client's balance per day/month.
  * <!--CLOSED_CORRECTION--> — corrective balance operations performed on the client's account per day/month.
  * <!--CLOSED_BONUS--> — bonus funds deposited/withdrawn from the account per day/month.
  * <!--CLOSED_COMMISSION_INSTANT--> — standard commissions withdrawn from a client's account per day/month instantly (during a trade).
  * <!--CLOSED_COMMISSION_ROUND--> — commission by orders and positions accumulated during a day/month. Depending on the settings (specified for the group in the administrator terminal), preliminary commission calculation is performed during a day/month and the appropriate funds are blocked in the account and displayed here. Final commission calculation is performed at the end of a day/month and the appropriate sum is withdrawn from the account by the balance operation.
  * <!--CLOSED_FEE--> — total fees charged from the client for the day/month.
  * <!--CLOSED_AGENT--> — agent commissions charged from the client for the day the report is generated for.
  * <!--CLOSED_INTEREST--> — annual interest rate accruals per day/month the report is generated for.
  * <!--CLOSED_DIVIDEND--> — dividends received by the client per day/month the report is generated for.
  * <!--CLOSED_TAX--> — taxes charged per day/month the report is generated for.
  * <!--CLOSED_PL--> — total profit/loss at a client's account per day/month the report is generated for. Calculated as <!--CLOSED_PROFIT--> \+ <!--CLOSED_STORAGE--> \+ <!--CLOSED_COMMISSION_INSTANT-->.
  * <!--CLOSED_ADDITIONAL--> — financial result of other transactions conducted on the account for the day/month the report is generated for. These are additional charges, corrections, bonuses, agent commissions, annual interests, dividends and taxes
  * <!--CLOSED_TOTAL--> — total financial result of the client's account for the day/month the report is generated for. Calculated as the sum of all the above values with the <!--CLOSED_*--> prefix apart from <!--CLOSED_PL--> and <!--CLOSED_ADDITIONAL-->.
  * <!--CLOSED_SO_COMPENSATION--> — the sum of balance operations connected with [the negative balance compensation (#compensate)](../../Platform-Setup/Groups/Group-Settings.md#compensate) after Stop Out.
  * <!--CLOSED_COST--> — the total amount of costs for all deals for the day/month for which the report is generated. The value calculation does not depend on [group settings (#deal-cost)](../../Platform-Setup/Groups/Group-Settings.md#deal-cost). If a macro is included in a report template, its value will be calculated and substituted.
  * <!--PREV_EQUITY_DIFF_PERC_DAILY--> — a change in equity as compared to the previous day value. Indicated as a percentage.
  * <!--PREV_EQUITY_DIFF_PERC_MONTHLY--> — a change in equity as compared to the previous month value. Indicated as a percentage.



<a id="macros-of-trading-operations"></a>
### Macros of Trading Operations (#macros-of-trading-operations)

Daily reports include blocks of trading operations performed by a client during a day/month. Each of these blocks begins with a macro corresponding to the operation type:

  * <!--MQTABLE=Closed Orders--> — closed orders.
  * <!--MQTABLE=Closed Deals--> — executed deals.
  * <!--MQTABLE=Positions--> — current open positions.
  * <!--MQTABLE=Orders--> — current open orders.



Each of these blocks ends with the <!--MQTABLE--> macro. Information about trading operations is displayed using macros inside the blocks. Depending on the block in which a macro is contained, it substitutes information about the appropriate operation type, i.e. order, deal or positions.

  * <!--Ticket--> — the ticket of a trading operation.
  * <!--Type--> — the type of a trading operation (buy, sell or a pending order).
  * <!--Size--> — the volume of a trading operation. The initial and filled volume is additionally displayed for orders.
  * <!--Item--> — the name of a trading instrument.
  * <!--ISIN--> — International Securities Identification Number (ISIN).
  * <!--Price--> — the price at which a trading operation was executed.
  * <!--SL--> — the Stop Loss level.
  * <!--TP--> — the Take Profit level.
  * <!--Open Time--> — operation time.
  * <!--Close Time--> — order or position closing time.
  * <!--State--> — order status (filled, rejected, canceled).
  * <!--Comment--> — a comment on the operation.
  * <!--Entry--> — trade direction (in, out, in/out).
  * <!--Commission--> — commission charged for the operation.
  * <!--Fee--> — the amount of fees for the operation.
  * <!--Swap--> — operation swap.
  * <!--Cost--> — the amount of costs incurred when performing deals relative to the current mid-point spread cost. The value calculation does not depend on [group settings (#deal-cost)](../../Platform-Setup/Groups/Group-Settings.md#deal-cost). If a macro is included in a report template, its value will be calculated and substituted.
  * <!--Profit--> — profit received from the operation.
  * <!--Market--> — the market price of a trading instrument at the time of report generation.
  * <!--Color--> — a macro for alternating the background color of even and odd rows (a row with a white background, the next one has a gray background, etc).



```

---

<a id='trade-server-return-errors-md'></a>
### 119. `Trade-Server/Return-Errors.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Trade Server](../Trade-Server.md) / Return Errors

[Previous](SendMail-Utility.md) | [Next](../Access-Server.md)

# Return Errors

When an attempt is made to perform invalid operations, a trade server returns errors to terminals. They are displayed on the ["Journal"](../../MetaTrader-5-Administrator/User-Interface/Toolbox/Journal.md) tab of the "Toolbox" window, as well as in [journals of servers](../../Platform-Setup/Network-cluster/Journal.md).

## Common Errors

Error | Description  
---|---  
Common error | Error not included to any of categories listed below.  
Invalid parameters | Incorrect parameters are specified at the attempt to change any of configurations.  
Disk error | This error occurs when it is impossible to write information on a disk.  
Memory error | This error indicates that there is not enough memory.  
Network error | This error is shown when a failure occurs in the network interaction of the platform components.  
Not enough permissions | This error occurs when a manager/administrator attempts to perform an action, for which he or she doesn't have enough [permissions (#permissions)](../../Platform-Setup/Managers.md#permissions).  
Operation timeout | The error means that the operation fulfillment waiting period is over.  
No connection | Connection to the server couldn't be established.  
Service is not available | This error can appear when information is requested from one of the platform components that is currently unavailable.  
Too frequent requests | The error occurs if requests to the server are made to often.  
Not found | Requested information was not found.  
  
## Authorization Errors

Error | Description  
---|---  
Invalid terminal type | This error can occur at the attempt to connect using a [manager](../../Platform-Setup/Managers.md) group account via the client terminal or vice versa - connect from manager/administrator terminal using an account from a common [group](../../Platform-Setup/Groups.md).  
Invalid account | This error appears if invalid account number or incorrect password are specified during [authorization](../../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server.md).  
Unknown account | This error appears if a user tries to authorize using an account that is created on a trade server, connection to which is [prohibited for the access server (#servers)](../../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md#servers). Due to it, the access server cannot identify the account and denies its connection.  
Account disabled | The error appears at the attempt to connect using a [disabled (#enable)](../../Platform-Setup/Accounts/Editing-Account.md#enable) account.  
Advanced authorization | This message indicates that the procedure of [extended authorization](../../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server/Extended-Authorization.md) must be performed for connecting.  
Certificate required | This message is shown at the attempt to to connect using the account that requires a SSL certificate to be generated in order to connect.  
Invalid certificate | This message appears at the attempt to connect using a certificate that is invalid for this account. For example, if it was [reset (#authorization)](../../Platform-Setup/Accounts/Editing-Account.md#authorization) on the server.  
Certificate is not confirmed | The message is shown at the attempt to connect using an [unconfirmed (#authorization)](../../Platform-Setup/Accounts/Editing-Account.md#authorization) certificate.  
Attempt to connect to non-access server | This error means that an attempt is made to connect to one of the platform components directly, bypassing the [access server](../Access-Server.md).  
Invalid or fake server | The error indicates that the server, to which there was an attempt to connect, is invalid.  
Only updates available | This error is shown when an attempt is made to connect to the [history server](../History-Server.md) at the time when only connecting to it for obtaining updates is allowed. This situation can appear during the platform update, when the server has been updated and is operating, but its configurations are not yet synchronized with the [main trade server](../Trade-Server.md).  
Old version | It indicates that the version of the component is old.  
Account doesn't have manager config | The error occurs at the attempt to connect using the account for which no [manager](../../Platform-Setup/Managers.md) configurations have been created.  
IP address unallowed for manager | The error occurs at the attempt of a manager connection from an [unallowed IP address (#access-list)](../../Platform-Setup/Managers.md#access-list).  
Group is not initialized | The error occurs at the attempt to create an account in the [group](../../Platform-Setup/Groups.md) that hasn't been initialized yet. In order to initialize a group after it has been created, the trade server needs to be [restarted](../../Platform-Setup/Network-cluster/Restarting-and-Stopping-Servers.md).  
Certificate generation disabled | The error occurs if the terminal requests generation of a new SSL certificate, but the possibility of their automatic generation is disabled on the server.  
  
## Configuration Management Errors

Error | Description  
---|---  
Last admin config deleting | The error appears at the attempt to delete the last [manager configuration](../../Platform-Setup/Managers.md).  
Last admin group cannot be deleted | The error appears at the attempt to delete the last administrator [group](../../Platform-Setup/Groups.md).  
Accounts or trades in group | The error appears at the attempt to delete a [group](../../Platform-Setup/Groups.md) that contains [accounts](../../Platform-Setup/Accounts.md) or [trade operations](../../Platform-Setup/Positions.md).  
Invalid accounts or trades ranges | The error appears at the attempt to set the range of [accounts (#accounts)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#accounts), [orders (#orders)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#orders) or [deals (#deals)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#deals) for a trade server that coincide with the same ranges on other servers.  
Account is not from manager group | The error occurs at the attempt to create a [manager configuration](../../Platform-Setup/Managers.md) based on the account that does not belong to the manager group.  
Built-in protected config | The error occurs at the attempt to delete a built-in configuration of collection of the server [performance parameters](../../Platform-Setup/Network-cluster/Monitor.md).   
Configuration duplicate | This error is shown when an attempt is made to add the second [main trade server](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md) or a [history server](../../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md) in the "Network" section.  
Configuration limit reached | This error appears at the attempt to create a new configuration, when the limit to their creation is reached. This can happen if the license was [not activated](../../Platform-Installation/Activation.md). In this case the number of [groups](../../Platform-Setup/Groups.md), for example, is limited to five.  
Invalid network configuration | This error appears at the attempt to save such [network settings](../../Platform-Setup/Network-cluster.md) that the administrator will not be able no connect to the main trade server.  
  
## Account Management Errors

Error | Description  
---|---  
Last admin account deleting | This error appears at the attempt to delete the last [manager](../../Platform-Setup/Managers.md) account.  
Logins range exhausted | The error appears at the attempt to create an account when the [range of allowed accounts (#accounts)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#accounts) was exhausted.  
Login reserved at another server | This error appears at the attempt to [create an account](../../Platform-Setup/Accounts/Creating-Account.md) via a manager or administrator terminal with the login that already exists on another server.  
Account already exists | The error appears at the attempt to [create an account](../../Platform-Setup/Accounts/Creating-Account.md) with already existing login.  
Attempt of self-deletion | The error appears if an administrator is trying to delete his or her own account via the administrator terminal.  
Invalid account password | The error appears if incorrect password was specified during [password verification (#password)](../../Platform-Setup/Accounts/Editing-Account.md#password).  
Users limit reached | The error appears at the attempt to create a new [account](../../Platform-Setup/Accounts.md) when their limit is over. The situation is possible when the license was [not activated](../../Platform-Installation/Activation.md).  
Account has open trades | The error appears at the attempt to delete an account with [open positions](../../Platform-Setup/Positions.md).  
Attempt to move account to different server | The error appears at the attempt to move an [account](../../Platform-Setup/Accounts.md) to the group that belongs to [another trade server (#trade-server)](../../Platform-Setup/Groups/Group-Settings.md#trade-server).  
Attempt to move account to different currency group | The error appears at the attempt to move an account to the group with a different [deposit currency (#currency)](../../Platform-Setup/Groups/Group-Settings.md#currency).  
  
## State of Trade Requests

Error | Description  
---|---  
Request on the way | The request has been sent to a server but it hasn't accepted it yet.  
Request accepted | The request has been accepted by the server and is waiting to be processed.  
Request processed | The server has started to process the request.  
Requote | Requoting as a reply to a client's request to execute a trade operation.  
Prices | Sending prices.  
Request rejected | The request is rejected by the server or dealer.  
Request canceled | the request was canceled by the server, dealer or client.  
Order placed | The order has been placed and is waiting till the specified processing conditions appear.  
Request executed | The requested operation has been executed.  
Request executed partly | The requested operation has been executed partially. E.g. a [deal](../../Platform-Setup/Deals.md) on the part of volume specified in the [order](../../Platform-Setup/Orders.md) is executed.  
Request error | Error of request execution.  
Request timeout | Time of request execution waiting is over.  
Invalid request | The request didn't pass the common validation procedure.  
Invalid volume | Incorrect volume is specified in the request.  
Invalid price | Incorrect price is specified in the request.  
Invalid stops | Incorrect Take Profit and Stop Loss levels are specified in the request.  
Trade disabled | Trading is [disabled (#trading)](../../Platform-Setup/Accounts/Editing-Account.md#trading) for this account.  
Market closed | The error appears at the attempt to execute trade operations beyond the allowed period (both [common trading hours (#daylight-saving)](../../Platform-Setup/Time.md#daylight-saving) and [trade sessions](../../Platform-Setup/Symbols/Symbol-Settings/Sessions.md) of separate symbols).  
No money | Attempt to execute a trade operations, when there is not enough money for its execution.  
Price changed | The error appears when the [maximal deviation (#max-deviation)](../../Platform-Setup/Symbols/Symbol-Settings/Execution.md#max-deviation) of the current price at the request price is exceeded.  
No prices | The error appears when there is no thread of quotes.  
Invalid expiration | The error occurs at the attempt to place an order with an incorrect [expiration (#expiration)](../../Platform-Setup/Orders.md#expiration) date.  
Order has been changed already | The error appears at the attempt to modify an order, which has been simultaneously modified.  
Too many trade requests | The error appears if trade requests are sent too often to the server.  
AutoTrading disabled by server | This error indicates that trading of [Expert Advisors (#ea-trading)](../../Platform-Setup/Accounts/Editing-Account.md#ea-trading) on this account is prohibited.  
AutoTrading disabled by client | This error indicates that trading of Expert Advisors is disabled in the client terminal.

```

---

<a id='trade-server-sendmail-utility-md'></a>
### 119. `Trade-Server/SendMail-Utility.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Trade Server](../Trade-Server.md) / SendMail Utility

[Previous](Daily-Reports.md) | [Next](Return-Errors.md)

# SendMail Utility

MetaTrader 5 SendMail is a command-line utility and a component of MetaTrader 5 platform. It is used by a trade server for sending reports and emails. This application can be used for sending reports manually.

## Report Generation

The trade server [prepares reports on (#end-of-day)](../../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#end-of-day) client deals at the end of a working day placing them to the separate directory ("/MetaTraderServer/confirms/YYYYMMDD", where YYYYMMDD is current date). Each report is an HTML file having the name "login_mail.htm" (for example, "123_mail.htm"). After generating all reports, the trade server saves the configuration file ("mail.cfg") containing descriptions of account groups with e-mail settings in the same directory and then launches MetaTrader 5 SendMail utility.

## Operation Principles

After launching MetaTrader 5, SendMail reads the configuration file and starts sending emails to account groups. Description of each group contains data that is sufficient for authorization on the specified SMTP server. In case of an authorization error, the program simply moves to the next group sending the appropriate error message to the journal. If authorization is successful, reports are consistently sent to these group's accounts.

Two types of errors may occur when sending reports. First, connection to the SMTP server may be lost. In this case, an attempt to handle the next group is made. Second, the server may report that it is not able to send a report to the specified client address (for example, if the latter is incorrect). In this case, the report is marked as unsent and handling is moved to the next one.

After all MetaTrader 5 groups are handled, SendMail records the results in the same configuration file. Then all the reports and the configuration file are compressed into a ZIP file. ZIP file's name is based on the name of a low-level folder in the path to the reports (for example, if the path is "C:\mt5\trade_server\confirms\20130101", then ZIP file's name is "20130101.zip"). After the successful archiving, all source files are deleted.

> Attention: We strongly recommend to use your own mail server (at least having the  name)

# Sending Reports Manually

Reports may be sent manually in two modes: group and individual ones. To choose the mode, one of the keys should additionally be specified in the command line when launching MetaTrader 5 SendMail:

  * mt5sendmail64.exe /mail:[path] — individual mailing.
  * mt5sendmail64.exe /group:[path] — group mailing.
  * /archive — specify this key after /mail:[path] or /group:[path] to force the SendMail archive the reports after sending.



### Individual Mailing

MetaTrader 5 SendMail with "mail" key should be launched to send a report to a single user:

mt5sendmail64.exe /mail:"path" /archive  
---  
  
Path is the path to the directory containing folder.cfg mailing configuration file (the file should have exactly the name mentioned above). Do not add a backslash at the end of the path:

mt5sendmail64.exe /mail: "C:\MetaTrader 5 Platform\MainTrade\confirms\2021.05.11.daily" /archive  
---  
  
Here is an example of a configuration file structure:

from=abc@company.net  
name=ABC Company  
subject=Trade Report  
to=johnsmith@mail.net  
to_name=John Smith  
charset=utf-8  
body=D:\Reports\John_Smith\mail.htm  
attachments=D:\Reports\John_Smith\balance.jpg  
smtp_srv=abc@company.net  
smtp_login=mailer  
smtp_pass=mailerpassword  
---  
  
The following parameters are specified in the configuration file:

  * from — e-mail address, from which the report is sent.
  * name — sender's name.
  * subject — email subject.
  * to — recipient's email address.
  * to_name — recipient's name.
  * charset — email's character set.
  * body — path to the HTM file containing the email's contents.
  * attachments — path to the file that is to be attached to the email. If you want to attach several files, specify paths to them divided by tab. The line length, including the parameter name, should not exceed 256 characters.
  * smtp_srv — SMTP server address used for sending messages.
  * smtp_login — login for authorization on the mail server. In most cases, it is a mailbox, for example, "your_name@mail.ru".
  * smtp_pass — password for authorization on the mail server (mailbox password).



  * Up to 8 attachments can be added to an email.
  * Attachment size may not exceed 4 MB.
  * The password for authorization on the SMTP server is stored in the clear. This is done in order to modify the configuration file easily. The administrator can change the configuration (for example, a password) and launch SendMail manually. For security purposes, it is recommended to limit access to report configuration files.

  
---  
  
### Group Mailing

MetaTrader 5 SendMail with "group" key should be launched to send a report to a group of users:

mt5sendmail64.exe /group:"path" /archive  
---  
  
Path is a path to mail.cfg file (the file should have exactly the name mentioned above) containing description of mailing settings.

> Report files being sent should be in the same directory with  configuration file. The report for each user should be in the form of an HTM file named  (for example, ).

Here is an example of a configuration file structure:

<group>  
name=demoforex  
company=MetaQuotes Software Corp.  
email=reporter@metaquotes.ru  
subject=Trade Report  
smtp_srv=mail.metaquotes.ru  
smtp_login=reporter  
smtp_pass=securepass  
  
101 1 John Smith jjohnsmith@mail.ru  
102 1 Ivan Ivanov ivan@mail.ru  
103 2 Larisa Ivanovna larisa@mail.ru  
</group>  
  
<group>  
name=forever  
company=MetaQuotes Software Corp.  
email=mailer@metaquotes.ru  
smtp_srv=mail.metaquotes.ru  
smtp_login=mailer  
smtp_pass=mailerpassword  
  
151 0 Alisa alisa@pole.ru  
152 0 Brom brom@fix.com  
153 0 SirX sirx@fix.com  
</group>  
---  
  
Each target user group is described by a couple of <group> tags. Description of each group contains several mandatory fields:

  * name — group name.
  * company — company name that will be specified as a sender's name.
  * email — e-mail address, on behalf of which the report is sent.
  * subject — email subject.
  * smtp_srv — SMTP server address used for sending messages.
  * smtp_login — login for authorization on the mail server. In most cases, it is a mailbox, for example, "your_name@mail.ru".
  * smtp_pass — password for authorization on the mail server (mailbox password).



> The password for authorization on the SMTP server is stored in the clear. This is done in order to modify the configuration file easily. The administrator can change the configuration (for example, a password) and launch SendMail manually. For security purposes, it is recommended to limit access to report configuration files.

The group's description is followed by the list of users that should receive the reports. The description and the list should be divided by an empty line used as a separator.

Each entry in the user list consists of the four fields: login, mailing status, recipient name and email. Tab character is used as a field separator. The first field may contain spaces before its contents. Let's examine a sample entry in more details:

102 1 Ivan Ivanov ivan@mail.ru  
---  
  
Status ID may have the following values:

  * 0 — report has not been sent or is on hold.
  * 1 — report has been sent successfully.
  * 2 — report delivery error, invalid recipient e-mail address.



After the reports have been sent, mailing status is updated in the same configuration file.

```

---

<a id='trade-server-structure-of-directories-and-files-md'></a>
### 119. `Trade-Server/Structure-of-Directories-and-Files.md`

```markdown
[🏠 Document Start](../../../README.md) / [MetaTrader 5 Trading Platform](../../../MetaTrader-5-Trading-Platform.md) / [Platform Components](../../Platform-Components.md) / [Trade Server](../Trade-Server.md) / Structure of Directories and Files

[Previous](../Trade-Server.md) | [Next](Mail-Templates.md)

# Structure of Directories and Files

The trade server is installed to the "Trade" folder. It contains the following executable files:

  * mt5srvupdater64.exe — the executable file of the live update system of the trade server;
  * mt5Trade64.exe — the executable file of the trade server;
  * mt5sendmail64.exe — the executable file of an [utility for sending reports](SendMail-Utility.md) via email.



The main server directory contains five folders: archive, bases, config, logs, templates.

The directory archive contains the database of accounts moved to the [archive](../../Platform-Setup/Accounts/Archive-and-Backup-Bases.md):

Files | Description  
---|---  
users_archive_yyyy.dat | Databases of archive users by years.  
users_archive_yyyy.idx | Index files of databases of archive users by years.  
  
The directory bases contains all databases of the trade server:

Files and folders | Description | Files | Description  
---|---|---|---  
deals\ | Database of [deals](../../Platform-Setup/Deals.md). | deals_yyyy.mm.dat | Databases of deals by months.  
deals_yyyy.mm.idx | Index files of databases of deals by months.  
history\ | Database of [order history](../../Platform-Setup/Orders.md) (filled, rejected, canceled and expired orders). | history_yyyy.mm.dat | Databases of order history by months.  
history_yyyy.mm.idx | Index files of databases of order history by months.  
mail\ | Email database. | mail_yyyy.mm.dat | Email databases by month.  
mail_yyyy.mm.idx | Index files of email databases by months.  
daily\ | The database of [daily reports](Daily-Reports.md). | daily_yyyy.mm.dat | Databases of daily reports by months.  
daily_yyyy.mm.idx | Index files of the daily report databases by months.  
crm\ | [Client](../../Platform-Setup/Clients.md) database. The client database itself, as well as the databases of [documents (#documents)](../../Platform-Setup/Clients.md#documents), [comments (#comments)](../../Platform-Setup/Clients.md#comments) and files are stored in subdirectories.  
performance\ | Monthly trade server performance databases and data indexes, which are displayed on the [Monitoring](../../Platform-Setup/Network-cluster/Monitor.md) tab.  
confirmation.dat | Database of [verified phone numbers and emails (#confirmation)](../../Platform-Setup/Accounts/Account-Allocation-Settings.md#confirmation).  
liveupdate.dat | Database of [live updates](../../Platform-Setup/Live-Update.md).  
orders.dat | Database of active [orders](../../Platform-Setup/Orders.md) (placed orders).  
orders.idx | The index file of the database of active orders.  
positions.dat | Database of [positions](../../Platform-Setup/Positions.md).  
positions.idx | The index file of the database of positions.  
users.dat | Database of [accounts](../../Platform-Setup/Accounts.md).  
daily.dat | Database of [daily reports](../../Platform-Setup/Reports/Daily.md).  
daily.idx | Index file of the daily report database.  
certificates.dat | Database of client certificates generated by the server for the [extended authorization (#security)](../../Platform-Setup/Accounts/Editing-Account.md#security). The server stores only the public part of the certificate, while the private part is stored only at the client's side.  
certificates.idx | Index file of the certificate database.  
executions.dat | Database of trade executions. More detailed information is available in the [MetaTrader 5 Gateway API user guide (#executions)](https://support.metaquotes.net/en/docs/mt5/api/gatewayapi_trade_processing#executions).  
kyc.dat | Database for storing the result of client verifications through external [KYC service providers](../../Platform-Setup/Integrations/KYC.md).  
geo.dat | Database for the operation of [geo services](https://support.metaquotes.net/en/docs/mt5/api/imtserverapi/serverapi_geo).  
  
The config directory contains all the server configurations in the form of encrypted *.ini files:

Files | Description  
---|---  
access.ini | Settings of [access by IP addresses](../../Platform-Setup/Security/Firewall.md).  
common.ini | Common server settings.  
feeders.ini | Settings of [data feeds](../../Platform-Setup/Data-Feeds.md).  
groups.ini | Settings of [groups](../../Platform-Setup/Groups.md).  
history_sync.ini | Settings of [synchronization of history data](../../Platform-Setup/Synchronization.md).  
holidays.ini | Settings of [holidays](../../Platform-Setup/Holidays.md).  
managers.ini | Settings of [managers](../../Platform-Setup/Managers.md).  
performance.ini | Settings of the [server performance](../../Platform-Setup/Network-cluster/Monitor.md) display.  
requests.ini | Settings of request [routing rules](../../Platform-Setup/Routing.md).  
server.ini | Individual server settings.  
servers.ini | Settings of the internal [network of servers](../../Platform-Setup/Network-cluster.md).  
symbol_groups.ini | Individual settings of [symbols for groups](../../Platform-Setup/Groups/Group-Symbol-Settings.md).  
symbols.ini | Settings of [symbols](../../Platform-Setup/Symbols.md).  
time.ini | [Time](../../Platform-Setup/Time.md) settings.  
license.lic | The license file.  
  
The logs directory contains the files of the server operation journal, as well as crash logs:

Folders and files | Description  
---|---  
Crash\crash.log.* | The /crash directory contains server crash files. These files are automatically sent to the software developing company for detecting reasons of the crash and eliminating them.  
yyyymmdd.log | [Journal](../../Platform-Setup/Network-cluster/Journal.md) files that contain all the information about events that occur on the trade server. Server logs are stored in separate files for each working day. Here yyyy — year, mm — month, dd — day.   
mt5srvupdater.log | Journal files of the platform [updates](../../Platform-Setup/Live-Update.md).  
  
The plugins directory contains DLL files of [plugins](../../Platform-Setup/Plugins.md) for the trade server written using the MetaTrader 5 Server API.

The templates directory contains two folders: "Certificate", "Confirmation", "Greeting" and "Statement". They contain [templates of emails](Mail-Templates.md) for certificate confirmation, templates of welcoming letters and templates for daily and monthly reports.

Subfolders | Description | Files | Description  
---|---|---|---  
Default\ | Folder of default email templates. | Default.html | Templates of default emails, that are used if templates corresponding to the user's language were not found.  
Users folder\ | Folder of templates of emails that can be sent to separate groups only according to their settings. | language_name.html | templates of emails by languages that are sent in accordance with the language specified by the user. E.g. English.html.  
  
The reports directory contains the DLL files of [reports](../../Platform-Setup/Reports.md) created using MetaTrader 5 Report API.

The confirms directory is used to prepare HTML files of [daily reports](../../Platform-Setup/Reports/Daily.md) before sending them to clients.

The settings directory stores [dashboard](https://support.metaquotes.net/en/docs/mt5/manager/analytics) and [filter (#filter)](https://support.metaquotes.net/en/docs/mt5/manager/accounts#filter) settings used in manager terminals. 

```

---
