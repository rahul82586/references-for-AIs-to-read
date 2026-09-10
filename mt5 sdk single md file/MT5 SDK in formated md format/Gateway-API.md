# 📁 Gateway-API

- **Generated:** 2026-09-09 00:09
- **Total Files:** 195
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\Gateway-API`

---

## 📑 Table of Contents

1. [CMTGatewayAPIFactory.md](#cmtgatewayapifactory-md)
2. [Development-and-Debugging-of-Gateways.md](#development-and-debugging-of-gateways-md)
3. [Development-of-Data-Feeds.md](#development-of-data-feeds-md)
4. [Event-Interface.md](#event-interface-md)
5. [Exported-Functions.md](#exported-functions-md)
6. [Interaction-of-the-Platform-and.md](#interaction-of-the-platform-and-md)
7. [Main-Interface.md](#main-interface-md)
8. [NET-Implementation.md](#net-implementation-md)
9. [README.md](#readme-md)
10. [Symbol-and-Price-Translation.md](#symbol-and-price-translation-md)
11. [Trade-Operations-in.md](#trade-operations-in-md)
12. [CMTGatewayAPIFactory/Create.md](#cmtgatewayapifactory-create-md)
13. [CMTGatewayAPIFactory/Initialize.md](#cmtgatewayapifactory-initialize-md)
14. [CMTGatewayAPIFactory/LicenseCheck.md](#cmtgatewayapifactory-licensecheck-md)
15. [CMTGatewayAPIFactory/Shutdown.md](#cmtgatewayapifactory-shutdown-md)
16. [CMTGatewayAPIFactory/Version.md](#cmtgatewayapifactory-version-md)
17. [Event-Interface/HookGatewayAccountRequest.md](#event-interface-hookgatewayaccountrequest-md)
18. [Event-Interface/HookGatewayOrdersRequest.md](#event-interface-hookgatewayordersrequest-md)
19. [Event-Interface/HookGatewayPositionsCheck.md](#event-interface-hookgatewaypositionscheck-md)
20. [Event-Interface/HookGatewayPositionsRequest.md](#event-interface-hookgatewaypositionsrequest-md)
21. [Event-Interface/HookServerConnect.md](#event-interface-hookserverconnect-md)
22. [Event-Interface/OnDealerAnswer.md](#event-interface-ondealeranswer-md)
23. [Event-Interface/OnDealerLock.md](#event-interface-ondealerlock-md)
24. [Event-Interface/OnGatewayAccountAnswer.md](#event-interface-ongatewayaccountanswer-md)
25. [Event-Interface/OnGatewayAccountSet.md](#event-interface-ongatewayaccountset-md)
26. [Event-Interface/OnGatewayConfig.md](#event-interface-ongatewayconfig-md)
27. [Event-Interface/OnGatewayShutdown.md](#event-interface-ongatewayshutdown-md)
28. [Event-Interface/OnGatewayStart.md](#event-interface-ongatewaystart-md)
29. [Event-Interface/OnGatewayStop.md](#event-interface-ongatewaystop-md)
30. [Event-Interface/OnServerDisconnect.md](#event-interface-onserverdisconnect-md)
31. [Event-Interface/OnServerSymbolAdd.md](#event-interface-onserversymboladd-md)
32. [Event-Interface/OnServerSymbolDelete.md](#event-interface-onserversymboldelete-md)
33. [Event-Interface/OnServerSynchronized.md](#event-interface-onserversynchronized-md)
34. [Exported-Functions/MTGatewayCreate.md](#exported-functions-mtgatewaycreate-md)
35. [Exported-Functions/MTGatewayCreateLocal.md](#exported-functions-mtgatewaycreatelocal-md)
36. [Exported-Functions/MTGatewayVersion.md](#exported-functions-mtgatewayversion-md)
37. [Main-Interface/Client-Connection.md](#main-interface-client-connection-md)
38. [Main-Interface/Common-Functions.md](#main-interface-common-functions-md)
39. [Main-Interface/Configuration-Databases.md](#main-interface-configuration-databases-md)
40. [Main-Interface/Controlling-Orders-in-External-System.md](#main-interface-controlling-orders-in-external-system-md)
41. [Main-Interface/Controlling-Positions-in-External-System.md](#main-interface-controlling-positions-in-external-system-md)
42. [Main-Interface/Enumerations.md](#main-interface-enumerations-md)
43. [Main-Interface/External-Connection-State.md](#main-interface-external-connection-state-md)
44. [Main-Interface/Gateway-Symbols.md](#main-interface-gateway-symbols-md)
45. [Main-Interface/History-Data.md](#main-interface-history-data-md)
46. [Main-Interface/Mail-Database.md](#main-interface-mail-database-md)
47. [Main-Interface/Processing-Trade-Requests.md](#main-interface-processing-trade-requests-md)
48. [Main-Interface/Quote-and-News-Feeds.md](#main-interface-quote-and-news-feeds-md)
49. [Main-Interface/Server.md](#main-interface-server-md)
50. [Main-Interface/Synchronizing-Trading-Data.md](#main-interface-synchronizing-trading-data-md)
51. [Main-Interface/Tick-Data.md](#main-interface-tick-data-md)
52. [Main-Interface/Trade-Databases.md](#main-interface-trade-databases-md)
53. [Main-Interface/Trade-Requests.md](#main-interface-trade-requests-md)
54. [Main-Interface/User-Settings.md](#main-interface-user-settings-md)
55. [Main-Interface/Users.md](#main-interface-users-md)
56. [Main-Interface/Client-Connection/ClientAdd.md](#main-interface-client-connection-clientadd-md)
57. [Main-Interface/Client-Connection/ClientAllowIP.md](#main-interface-client-connection-clientallowip-md)
58. [Main-Interface/Common-Functions/Allocate.md](#main-interface-common-functions-allocate-md)
59. [Main-Interface/Common-Functions/Free.md](#main-interface-common-functions-free-md)
60. [Main-Interface/Common-Functions/LicenseCheck.md](#main-interface-common-functions-licensecheck-md)
61. [Main-Interface/Common-Functions/LoggerFlush.md](#main-interface-common-functions-loggerflush-md)
62. [Main-Interface/Common-Functions/LoggerOut.md](#main-interface-common-functions-loggerout-md)
63. [Main-Interface/Common-Functions/LoggerOutString.md](#main-interface-common-functions-loggeroutstring-md)
64. [Main-Interface/Common-Functions/Release.md](#main-interface-common-functions-release-md)
65. [Main-Interface/Configuration-Databases/Common.md](#main-interface-configuration-databases-common-md)
66. [Main-Interface/Configuration-Databases/Data-Feeds.md](#main-interface-configuration-databases-data-feeds-md)
67. [Main-Interface/Configuration-Databases/Gateways.md](#main-interface-configuration-databases-gateways-md)
68. [Main-Interface/Configuration-Databases/Groups.md](#main-interface-configuration-databases-groups-md)
69. [Main-Interface/Configuration-Databases/Network.md](#main-interface-configuration-databases-network-md)
70. [Main-Interface/Configuration-Databases/Spreads.md](#main-interface-configuration-databases-spreads-md)
71. [Main-Interface/Configuration-Databases/Symbols.md](#main-interface-configuration-databases-symbols-md)
72. [Main-Interface/Configuration-Databases/Time.md](#main-interface-configuration-databases-time-md)
73. [Main-Interface/Configuration-Databases/Common/Create.md](#main-interface-configuration-databases-common-create-md)
74. [Main-Interface/Configuration-Databases/Common/Get.md](#main-interface-configuration-databases-common-get-md)
75. [Main-Interface/Configuration-Databases/Common/Subscribe.md](#main-interface-configuration-databases-common-subscribe-md)
76. [Main-Interface/Configuration-Databases/Common/Unsubscribe.md](#main-interface-configuration-databases-common-unsubscribe-md)
77. [Main-Interface/Configuration-Databases/Data-Feeds/FeederCreate.md](#main-interface-configuration-databases-data-feeds-feedercreate-md)
78. [Main-Interface/Configuration-Databases/Data-Feeds/FeederParamCreate.md](#main-interface-configuration-databases-data-feeds-feederparamcreate-md)
79. [Main-Interface/Configuration-Databases/Data-Feeds/FeederTranslateCreate.md](#main-interface-configuration-databases-data-feeds-feedertranslatecreate-md)
80. [Main-Interface/Configuration-Databases/Gateways/GatewayCreate.md](#main-interface-configuration-databases-gateways-gatewaycreate-md)
81. [Main-Interface/Configuration-Databases/Gateways/GatewayParamCreate.md](#main-interface-configuration-databases-gateways-gatewayparamcreate-md)
82. [Main-Interface/Configuration-Databases/Gateways/GatewayTranslateCreate.md](#main-interface-configuration-databases-gateways-gatewaytranslatecreate-md)
83. [Main-Interface/Configuration-Databases/Groups/GroupCommissionCreate.md](#main-interface-configuration-databases-groups-groupcommissioncreate-md)
84. [Main-Interface/Configuration-Databases/Groups/GroupCreate.md](#main-interface-configuration-databases-groups-groupcreate-md)
85. [Main-Interface/Configuration-Databases/Groups/GroupGet.md](#main-interface-configuration-databases-groups-groupget-md)
86. [Main-Interface/Configuration-Databases/Groups/GroupNext.md](#main-interface-configuration-databases-groups-groupnext-md)
87. [Main-Interface/Configuration-Databases/Groups/GroupSubscribe.md](#main-interface-configuration-databases-groups-groupsubscribe-md)
88. [Main-Interface/Configuration-Databases/Groups/GroupSymbolCreate.md](#main-interface-configuration-databases-groups-groupsymbolcreate-md)
89. [Main-Interface/Configuration-Databases/Groups/GroupTierCreate.md](#main-interface-configuration-databases-groups-grouptiercreate-md)
90. [Main-Interface/Configuration-Databases/Groups/GroupTotal.md](#main-interface-configuration-databases-groups-grouptotal-md)
91. [Main-Interface/Configuration-Databases/Groups/GroupUnsubscribe.md](#main-interface-configuration-databases-groups-groupunsubscribe-md)
92. [Main-Interface/Configuration-Databases/Network/NetServerCreate.md](#main-interface-configuration-databases-network-netservercreate-md)
93. [Main-Interface/Configuration-Databases/Network/NetServerGet.md](#main-interface-configuration-databases-network-netserverget-md)
94. [Main-Interface/Configuration-Databases/Network/NetServerNext.md](#main-interface-configuration-databases-network-netservernext-md)
95. [Main-Interface/Configuration-Databases/Network/NetServerRangeCreate.md](#main-interface-configuration-databases-network-netserverrangecreate-md)
96. [Main-Interface/Configuration-Databases/Network/NetServerSubscribe.md](#main-interface-configuration-databases-network-netserversubscribe-md)
97. [Main-Interface/Configuration-Databases/Network/NetServerTotal.md](#main-interface-configuration-databases-network-netservertotal-md)
98. [Main-Interface/Configuration-Databases/Network/NetServerUnsubscribe.md](#main-interface-configuration-databases-network-netserverunsubscribe-md)
99. [Main-Interface/Configuration-Databases/Spreads/SpreadAdd.md](#main-interface-configuration-databases-spreads-spreadadd-md)
100. [Main-Interface/Configuration-Databases/Spreads/SpreadCreate.md](#main-interface-configuration-databases-spreads-spreadcreate-md)
101. [Main-Interface/Configuration-Databases/Spreads/SpreadDelete.md](#main-interface-configuration-databases-spreads-spreaddelete-md)
102. [Main-Interface/Configuration-Databases/Spreads/SpreadGet.md](#main-interface-configuration-databases-spreads-spreadget-md)
103. [Main-Interface/Configuration-Databases/Spreads/SpreadLegCreate.md](#main-interface-configuration-databases-spreads-spreadlegcreate-md)
104. [Main-Interface/Configuration-Databases/Spreads/SpreadNext.md](#main-interface-configuration-databases-spreads-spreadnext-md)
105. [Main-Interface/Configuration-Databases/Spreads/SpreadShift.md](#main-interface-configuration-databases-spreads-spreadshift-md)
106. [Main-Interface/Configuration-Databases/Spreads/SpreadSubscribe.md](#main-interface-configuration-databases-spreads-spreadsubscribe-md)
107. [Main-Interface/Configuration-Databases/Spreads/SpreadTotal.md](#main-interface-configuration-databases-spreads-spreadtotal-md)
108. [Main-Interface/Configuration-Databases/Spreads/SpreadUnsubscribe.md](#main-interface-configuration-databases-spreads-spreadunsubscribe-md)
109. [Main-Interface/Configuration-Databases/Symbols/SymbolAddPreliminary.md](#main-interface-configuration-databases-symbols-symboladdpreliminary-md)
110. [Main-Interface/Configuration-Databases/Symbols/SymbolCreate.md](#main-interface-configuration-databases-symbols-symbolcreate-md)
111. [Main-Interface/Configuration-Databases/Symbols/SymbolDelete.md](#main-interface-configuration-databases-symbols-symboldelete-md)
112. [Main-Interface/Configuration-Databases/Symbols/SymbolGet.md](#main-interface-configuration-databases-symbols-symbolget-md)
113. [Main-Interface/Configuration-Databases/Symbols/SymbolNext.md](#main-interface-configuration-databases-symbols-symbolnext-md)
114. [Main-Interface/Configuration-Databases/Symbols/SymbolSessionCreate.md](#main-interface-configuration-databases-symbols-symbolsessioncreate-md)
115. [Main-Interface/Configuration-Databases/Symbols/SymbolSubscribe.md](#main-interface-configuration-databases-symbols-symbolsubscribe-md)
116. [Main-Interface/Configuration-Databases/Symbols/SymbolTotal.md](#main-interface-configuration-databases-symbols-symboltotal-md)
117. [Main-Interface/Configuration-Databases/Symbols/SymbolUnsubscribe.md](#main-interface-configuration-databases-symbols-symbolunsubscribe-md)
118. [Main-Interface/Configuration-Databases/Symbols/SymbolUpdate.md](#main-interface-configuration-databases-symbols-symbolupdate-md)
119. [Main-Interface/Configuration-Databases/Time/Create.md](#main-interface-configuration-databases-time-create-md)
120. [Main-Interface/Configuration-Databases/Time/Current.md](#main-interface-configuration-databases-time-current-md)
121. [Main-Interface/Configuration-Databases/Time/Get.md](#main-interface-configuration-databases-time-get-md)
122. [Main-Interface/Configuration-Databases/Time/Subscribe.md](#main-interface-configuration-databases-time-subscribe-md)
123. [Main-Interface/Configuration-Databases/Time/Unsubscribe.md](#main-interface-configuration-databases-time-unsubscribe-md)
124. [Main-Interface/Controlling-Orders-in-External-System/GatewayOrderArrayCreate.md](#main-interface-controlling-orders-in-external-system-gatewayorderarraycreate-md)
125. [Main-Interface/Controlling-Orders-in-External-System/GatewayOrdersAnswer.md](#main-interface-controlling-orders-in-external-system-gatewayordersanswer-md)
126. [Main-Interface/Controlling-Positions-in-External-System/GatewayParamArrayCreate.md](#main-interface-controlling-positions-in-external-system-gatewayparamarraycreate-md)
127. [Main-Interface/Controlling-Positions-in-External-System/GatewayPositionArrayCreate.md](#main-interface-controlling-positions-in-external-system-gatewaypositionarraycreate-md)
128. [Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md](#main-interface-controlling-positions-in-external-system-gatewaypositionsanswer-md)
129. [Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsCheck.md](#main-interface-controlling-positions-in-external-system-gatewaypositionscheck-md)
130. [Main-Interface/External-Connection-State/StateConnect.md](#main-interface-external-connection-state-stateconnect-md)
131. [Main-Interface/External-Connection-State/StateTraffic.md](#main-interface-external-connection-state-statetraffic-md)
132. [Main-Interface/Gateway-Symbols/GatewaySymbolAdd.md](#main-interface-gateway-symbols-gatewaysymboladd-md)
133. [Main-Interface/Gateway-Symbols/GatewaySymbolClear.md](#main-interface-gateway-symbols-gatewaysymbolclear-md)
134. [Main-Interface/Gateway-Symbols/GatewaySymbolDelete.md](#main-interface-gateway-symbols-gatewaysymboldelete-md)
135. [Main-Interface/Gateway-Symbols/GatewaySymbolGet.md](#main-interface-gateway-symbols-gatewaysymbolget-md)
136. [Main-Interface/Gateway-Symbols/GatewaySymbolNext.md](#main-interface-gateway-symbols-gatewaysymbolnext-md)
137. [Main-Interface/Gateway-Symbols/GatewaySymbolTotal.md](#main-interface-gateway-symbols-gatewaysymboltotal-md)
138. [Main-Interface/History-Data/ChartDelete.md](#main-interface-history-data-chartdelete-md)
139. [Main-Interface/History-Data/ChartReplace.md](#main-interface-history-data-chartreplace-md)
140. [Main-Interface/History-Data/ChartRequest.md](#main-interface-history-data-chartrequest-md)
141. [Main-Interface/History-Data/ChartUpdate.md](#main-interface-history-data-chartupdate-md)
142. [Main-Interface/Mail-Database/MailCreate.md](#main-interface-mail-database-mailcreate-md)
143. [Main-Interface/Mail-Database/MailSend.md](#main-interface-mail-database-mailsend-md)
144. [Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md](#main-interface-processing-trade-requests-dealeranswerasync-md)
145. [Main-Interface/Processing-Trade-Requests/DealerConfirmCreate.md](#main-interface-processing-trade-requests-dealerconfirmcreate-md)
146. [Main-Interface/Processing-Trade-Requests/DealerExecuteAsync.md](#main-interface-processing-trade-requests-dealerexecuteasync-md)
147. [Main-Interface/Processing-Trade-Requests/DealerExecutionCreate.md](#main-interface-processing-trade-requests-dealerexecutioncreate-md)
148. [Main-Interface/Processing-Trade-Requests/DealerGetAsync.md](#main-interface-processing-trade-requests-dealergetasync-md)
149. [Main-Interface/Processing-Trade-Requests/DealerLockAsync.md](#main-interface-processing-trade-requests-dealerlockasync-md)
150. [Main-Interface/Processing-Trade-Requests/DealerStart.md](#main-interface-processing-trade-requests-dealerstart-md)
151. [Main-Interface/Processing-Trade-Requests/DealerStop.md](#main-interface-processing-trade-requests-dealerstop-md)
152. [Main-Interface/Quote-and-News-Feeds/SendBookDiffs.md](#main-interface-quote-and-news-feeds-sendbookdiffs-md)
153. [Main-Interface/Quote-and-News-Feeds/SendBooks.md](#main-interface-quote-and-news-feeds-sendbooks-md)
154. [Main-Interface/Quote-and-News-Feeds/SendEconomicEvents.md](#main-interface-quote-and-news-feeds-sendeconomicevents-md)
155. [Main-Interface/Quote-and-News-Feeds/SendNews.md](#main-interface-quote-and-news-feeds-sendnews-md)
156. [Main-Interface/Quote-and-News-Feeds/SendTickStats.md](#main-interface-quote-and-news-feeds-sendtickstats-md)
157. [Main-Interface/Quote-and-News-Feeds/SendTicks.md](#main-interface-quote-and-news-feeds-sendticks-md)
158. [Main-Interface/Server/Connections.md](#main-interface-server-connections-md)
159. [Main-Interface/Server/IP.md](#main-interface-server-ip-md)
160. [Main-Interface/Server/Port.md](#main-interface-server-port-md)
161. [Main-Interface/Server/Start.md](#main-interface-server-start-md)
162. [Main-Interface/Server/Stop.md](#main-interface-server-stop-md)
163. [Main-Interface/Synchronizing-Trading-Data/GatewayAccountAnswer.md](#main-interface-synchronizing-trading-data-gatewayaccountanswer-md)
164. [Main-Interface/Synchronizing-Trading-Data/GatewayAccountRequest.md](#main-interface-synchronizing-trading-data-gatewayaccountrequest-md)
165. [Main-Interface/Synchronizing-Trading-Data/GatewayAccountSet.md](#main-interface-synchronizing-trading-data-gatewayaccountset-md)
166. [Main-Interface/Tick-Data/TickHistoryAdd.md](#main-interface-tick-data-tickhistoryadd-md)
167. [Main-Interface/Tick-Data/TickHistoryReplace.md](#main-interface-tick-data-tickhistoryreplace-md)
168. [Main-Interface/Tick-Data/TickHistoryRequest.md](#main-interface-tick-data-tickhistoryrequest-md)
169. [Main-Interface/Tick-Data/TickHistoryRequestRaw.md](#main-interface-tick-data-tickhistoryrequestraw-md)
170. [Main-Interface/Trade-Databases/OrderCreate.md](#main-interface-trade-databases-ordercreate-md)
171. [Main-Interface/Trade-Databases/PositionCreate.md](#main-interface-trade-databases-positioncreate-md)
172. [Main-Interface/Trade-Requests/RequestArrayCreate.md](#main-interface-trade-requests-requestarraycreate-md)
173. [Main-Interface/Trade-Requests/RequestCreate.md](#main-interface-trade-requests-requestcreate-md)
174. [Main-Interface/Trade-Requests/RequestGet.md](#main-interface-trade-requests-requestget-md)
175. [Main-Interface/Trade-Requests/RequestGetAll.md](#main-interface-trade-requests-requestgetall-md)
176. [Main-Interface/Trade-Requests/RequestNext.md](#main-interface-trade-requests-requestnext-md)
177. [Main-Interface/Trade-Requests/RequestSubscribe.md](#main-interface-trade-requests-requestsubscribe-md)
178. [Main-Interface/Trade-Requests/RequestTotal.md](#main-interface-trade-requests-requesttotal-md)
179. [Main-Interface/Trade-Requests/RequestUnsubscribe.md](#main-interface-trade-requests-requestunsubscribe-md)
180. [Main-Interface/User-Settings/SettingsAdd.md](#main-interface-user-settings-settingsadd-md)
181. [Main-Interface/User-Settings/SettingsClear.md](#main-interface-user-settings-settingsclear-md)
182. [Main-Interface/User-Settings/SettingsDelete.md](#main-interface-user-settings-settingsdelete-md)
183. [Main-Interface/User-Settings/SettingsGet.md](#main-interface-user-settings-settingsget-md)
184. [Main-Interface/User-Settings/SettingsNext.md](#main-interface-user-settings-settingsnext-md)
185. [Main-Interface/User-Settings/SettingsTotal.md](#main-interface-user-settings-settingstotal-md)
186. [Main-Interface/User-Settings/SettingsUpdate.md](#main-interface-user-settings-settingsupdate-md)
187. [Main-Interface/Users/UserCreate.md](#main-interface-users-usercreate-md)
188. [Main-Interface/Users/UserCreateAccount.md](#main-interface-users-usercreateaccount-md)
189. [Main-Interface/Users/UserGet.md](#main-interface-users-userget-md)
190. [Main-Interface/Users/UserGetByAccount.md](#main-interface-users-usergetbyaccount-md)
191. [Main-Interface/Users/UserGroup.md](#main-interface-users-usergroup-md)
192. [Main-Interface/Users/UserLogins.md](#main-interface-users-userlogins-md)
193. [Main-Interface/Users/UserSubscribe.md](#main-interface-users-usersubscribe-md)
194. [Main-Interface/Users/UserTotal.md](#main-interface-users-usertotal-md)
195. [Main-Interface/Users/UserUnsubscribe.md](#main-interface-users-userunsubscribe-md)

---

## 🌲 Project Structure

```
Gateway-API/
├── CMTGatewayAPIFactory/
│   ├── Create.md
│   ├── images/
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
│   ├── Initialize.md
│   ├── LicenseCheck.md
│   ├── Shutdown.md
│   └── Version.md
├── CMTGatewayAPIFactory.md
├── Development-and-Debugging-of-Gateways.md
├── Development-of-Data-Feeds.md
├── Event-Interface/
│   ├── HookGatewayAccountRequest.md
│   ├── HookGatewayOrdersRequest.md
│   ├── HookGatewayPositionsCheck.md
│   ├── HookGatewayPositionsRequest.md
│   ├── HookServerConnect.md
│   ├── images/
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_10.png
│   │   ├── next_11.png
│   │   ├── next_12.png
│   │   ├── next_13.png
│   │   ├── next_14.png
│   │   ├── next_15.png
│   │   ├── next_16.png
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
│   │   ├── previous_2.png
│   │   ├── previous_3.png
│   │   ├── previous_4.png
│   │   ├── previous_5.png
│   │   ├── previous_6.png
│   │   ├── previous_7.png
│   │   ├── previous_8.png
│   │   └── previous_9.png
│   ├── OnDealerAnswer.md
│   ├── OnDealerLock.md
│   ├── OnGatewayAccountAnswer.md
│   ├── OnGatewayAccountSet.md
│   ├── OnGatewayConfig.md
│   ├── OnGatewayShutdown.md
│   ├── OnGatewayStart.md
│   ├── OnGatewayStop.md
│   ├── OnServerDisconnect.md
│   ├── OnServerSymbolAdd.md
│   ├── OnServerSymbolDelete.md
│   └── OnServerSynchronized.md
├── Event-Interface.md
├── Exported-Functions/
│   ├── images/
│   │   ├── next.png
│   │   ├── next_1.png
│   │   ├── next_2.png
│   │   ├── previous.png
│   │   ├── previous_1.png
│   │   └── previous_2.png
│   ├── MTGatewayCreate.md
│   ├── MTGatewayCreateLocal.md
│   └── MTGatewayVersion.md
├── Exported-Functions.md
├── images/
│   ├── datafeed_scheme.png
│   ├── datafeed_showcase.png
│   ├── gateway_showcase.png
│   ├── next.png
│   ├── next_1.png
│   ├── next_2.png
│   ├── next_3.png
│   ├── next_4.png
│   ├── next_5.png
│   ├── next_6.png
│   ├── next_7.png
│   ├── next_8.png
│   ├── next_9.png
│   ├── previous.png
│   ├── previous_1.png
│   ├── previous_10.png
│   ├── previous_2.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   ├── previous_6.png
│   ├── previous_7.png
│   ├── previous_8.png
│   ├── previous_9.png
│   ├── sample_gateway_common.png
│   ├── sample_gateway_debug.png
│   ├── sample_gateway_remote.png
│   ├── sample_gateway_routing_common.png
│   ├── sample_gateway_routing_dealers.png
│   ├── sample_gateway_scheme.png
│   ├── sample_gateway_symbols.png
│   ├── translation_price.png
│   ├── translation_price_split.png
│   ├── translation_split.png
│   ├── translations_rename.png
│   ├── translations_rename_mass.png
│   └── translations_trade_map.png
├── Interaction-of-the-Platform-and.md
├── Main-Interface/
│   ├── Client-Connection/
│   │   ├── ClientAdd.md
│   │   ├── ClientAllowIP.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── previous.png
│   │       └── previous_1.png
│   ├── Client-Connection.md
│   ├── Common-Functions/
│   │   ├── Allocate.md
│   │   ├── Free.md
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── next_5.png
│   │   │   ├── next_6.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_4.png
│   │   │   ├── previous_5.png
│   │   │   └── previous_6.png
│   │   ├── LicenseCheck.md
│   │   ├── LoggerFlush.md
│   │   ├── LoggerOut.md
│   │   ├── LoggerOutString.md
│   │   └── Release.md
│   ├── Common-Functions.md
│   ├── Configuration-Databases/
│   │   ├── Common/
│   │   │   ├── Create.md
│   │   │   ├── Get.md
│   │   │   ├── images/
│   │   │   │   ├── next.png
│   │   │   │   ├── next_1.png
│   │   │   │   ├── next_2.png
│   │   │   │   ├── next_3.png
│   │   │   │   ├── previous.png
│   │   │   │   ├── previous_1.png
│   │   │   │   ├── previous_2.png
│   │   │   │   └── previous_3.png
│   │   │   ├── Subscribe.md
│   │   │   └── Unsubscribe.md
│   │   ├── Common.md
│   │   ├── Data-Feeds/
│   │   │   ├── FeederCreate.md
│   │   │   ├── FeederParamCreate.md
│   │   │   ├── FeederTranslateCreate.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       ├── next_1.png
│   │   │       ├── next_2.png
│   │   │       ├── previous.png
│   │   │       ├── previous_1.png
│   │   │       └── previous_2.png
│   │   ├── Data-Feeds.md
│   │   ├── Gateways/
│   │   │   ├── GatewayCreate.md
│   │   │   ├── GatewayParamCreate.md
│   │   │   ├── GatewayTranslateCreate.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       ├── next_1.png
│   │   │       ├── next_2.png
│   │   │       ├── previous.png
│   │   │       ├── previous_1.png
│   │   │       └── previous_2.png
│   │   ├── Gateways.md
│   │   ├── Groups/
│   │   │   ├── GroupCommissionCreate.md
│   │   │   ├── GroupCreate.md
│   │   │   ├── GroupGet.md
│   │   │   ├── GroupNext.md
│   │   │   ├── GroupSubscribe.md
│   │   │   ├── GroupSymbolCreate.md
│   │   │   ├── GroupTierCreate.md
│   │   │   ├── GroupTotal.md
│   │   │   ├── GroupUnsubscribe.md
│   │   │   └── images/
│   │   │       ├── next.png
│   │   │       ├── next_1.png
│   │   │       ├── next_2.png
│   │   │       ├── next_3.png
│   │   │       ├── next_4.png
│   │   │       ├── next_5.png
│   │   │       ├── next_6.png
│   │   │       ├── next_7.png
│   │   │       ├── next_8.png
│   │   │       ├── previous.png
│   │   │       ├── previous_1.png
│   │   │       ├── previous_2.png
│   │   │       ├── previous_3.png
│   │   │       ├── previous_4.png
│   │   │       ├── previous_5.png
│   │   │       ├── previous_6.png
│   │   │       ├── previous_7.png
│   │   │       └── previous_8.png
│   │   ├── Groups.md
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── next_5.png
│   │   │   ├── next_6.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_4.png
│   │   │   ├── previous_5.png
│   │   │   ├── previous_6.png
│   │   │   └── previous_7.png
│   │   ├── Network/
│   │   │   ├── images/
│   │   │   │   ├── next.png
│   │   │   │   ├── next_1.png
│   │   │   │   ├── next_2.png
│   │   │   │   ├── next_3.png
│   │   │   │   ├── next_4.png
│   │   │   │   ├── next_5.png
│   │   │   │   ├── next_6.png
│   │   │   │   ├── previous.png
│   │   │   │   ├── previous_1.png
│   │   │   │   ├── previous_2.png
│   │   │   │   ├── previous_3.png
│   │   │   │   ├── previous_4.png
│   │   │   │   ├── previous_5.png
│   │   │   │   └── previous_6.png
│   │   │   ├── NetServerCreate.md
│   │   │   ├── NetServerGet.md
│   │   │   ├── NetServerNext.md
│   │   │   ├── NetServerRangeCreate.md
│   │   │   ├── NetServerSubscribe.md
│   │   │   ├── NetServerTotal.md
│   │   │   └── NetServerUnsubscribe.md
│   │   ├── Network.md
│   │   ├── Spreads/
│   │   │   ├── images/
│   │   │   │   ├── next.png
│   │   │   │   ├── next_1.png
│   │   │   │   ├── next_2.png
│   │   │   │   ├── next_3.png
│   │   │   │   ├── next_4.png
│   │   │   │   ├── next_5.png
│   │   │   │   ├── next_6.png
│   │   │   │   ├── next_7.png
│   │   │   │   ├── next_8.png
│   │   │   │   ├── next_9.png
│   │   │   │   ├── previous.png
│   │   │   │   ├── previous_1.png
│   │   │   │   ├── previous_2.png
│   │   │   │   ├── previous_3.png
│   │   │   │   ├── previous_4.png
│   │   │   │   ├── previous_5.png
│   │   │   │   ├── previous_6.png
│   │   │   │   ├── previous_7.png
│   │   │   │   ├── previous_8.png
│   │   │   │   └── previous_9.png
│   │   │   ├── SpreadAdd.md
│   │   │   ├── SpreadCreate.md
│   │   │   ├── SpreadDelete.md
│   │   │   ├── SpreadGet.md
│   │   │   ├── SpreadLegCreate.md
│   │   │   ├── SpreadNext.md
│   │   │   ├── SpreadShift.md
│   │   │   ├── SpreadSubscribe.md
│   │   │   ├── SpreadTotal.md
│   │   │   └── SpreadUnsubscribe.md
│   │   ├── Spreads.md
│   │   ├── Symbols/
│   │   │   ├── images/
│   │   │   │   ├── next.png
│   │   │   │   ├── next_1.png
│   │   │   │   ├── next_2.png
│   │   │   │   ├── next_3.png
│   │   │   │   ├── next_4.png
│   │   │   │   ├── next_5.png
│   │   │   │   ├── next_6.png
│   │   │   │   ├── next_7.png
│   │   │   │   ├── next_8.png
│   │   │   │   ├── next_9.png
│   │   │   │   ├── previous.png
│   │   │   │   ├── previous_1.png
│   │   │   │   ├── previous_2.png
│   │   │   │   ├── previous_3.png
│   │   │   │   ├── previous_4.png
│   │   │   │   ├── previous_5.png
│   │   │   │   ├── previous_6.png
│   │   │   │   ├── previous_7.png
│   │   │   │   ├── previous_8.png
│   │   │   │   └── previous_9.png
│   │   │   ├── SymbolAddPreliminary.md
│   │   │   ├── SymbolCreate.md
│   │   │   ├── SymbolDelete.md
│   │   │   ├── SymbolGet.md
│   │   │   ├── SymbolNext.md
│   │   │   ├── SymbolSessionCreate.md
│   │   │   ├── SymbolSubscribe.md
│   │   │   ├── SymbolTotal.md
│   │   │   ├── SymbolUnsubscribe.md
│   │   │   └── SymbolUpdate.md
│   │   ├── Symbols.md
│   │   ├── Time/
│   │   │   ├── Create.md
│   │   │   ├── Current.md
│   │   │   ├── Get.md
│   │   │   ├── images/
│   │   │   │   ├── next.png
│   │   │   │   ├── next_1.png
│   │   │   │   ├── next_2.png
│   │   │   │   ├── next_3.png
│   │   │   │   ├── next_4.png
│   │   │   │   ├── previous.png
│   │   │   │   ├── previous_1.png
│   │   │   │   ├── previous_2.png
│   │   │   │   ├── previous_3.png
│   │   │   │   └── previous_4.png
│   │   │   ├── Subscribe.md
│   │   │   └── Unsubscribe.md
│   │   └── Time.md
│   ├── Configuration-Databases.md
│   ├── Controlling-Orders-in-External-System/
│   │   ├── GatewayOrderArrayCreate.md
│   │   ├── GatewayOrdersAnswer.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── previous.png
│   │       └── previous_1.png
│   ├── Controlling-Orders-in-External-System.md
│   ├── Controlling-Positions-in-External-System/
│   │   ├── GatewayParamArrayCreate.md
│   │   ├── GatewayPositionArrayCreate.md
│   │   ├── GatewayPositionsAnswer.md
│   │   ├── GatewayPositionsCheck.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── next_2.png
│   │       ├── next_3.png
│   │       ├── previous.png
│   │       ├── previous_1.png
│   │       ├── previous_2.png
│   │       └── previous_3.png
│   ├── Controlling-Positions-in-External-System.md
│   ├── Enumerations.md
│   ├── External-Connection-State/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── previous.png
│   │   │   └── previous_1.png
│   │   ├── StateConnect.md
│   │   └── StateTraffic.md
│   ├── External-Connection-State.md
│   ├── Gateway-Symbols/
│   │   ├── GatewaySymbolAdd.md
│   │   ├── GatewaySymbolClear.md
│   │   ├── GatewaySymbolDelete.md
│   │   ├── GatewaySymbolGet.md
│   │   ├── GatewaySymbolNext.md
│   │   ├── GatewaySymbolTotal.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── next_2.png
│   │       ├── next_3.png
│   │       ├── next_4.png
│   │       ├── next_5.png
│   │       ├── previous.png
│   │       ├── previous_1.png
│   │       ├── previous_2.png
│   │       ├── previous_3.png
│   │       ├── previous_4.png
│   │       └── previous_5.png
│   ├── Gateway-Symbols.md
│   ├── History-Data/
│   │   ├── ChartDelete.md
│   │   ├── ChartReplace.md
│   │   ├── ChartRequest.md
│   │   ├── ChartUpdate.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── next_2.png
│   │       ├── next_3.png
│   │       ├── previous.png
│   │       ├── previous_1.png
│   │       ├── previous_2.png
│   │       └── previous_3.png
│   ├── History-Data.md
│   ├── images/
│   │   ├── admin_datafeed_state.png
│   │   ├── datafeed_timeouts.png
│   │   ├── gateway_positions.png
│   │   ├── gateway_synchronize.png
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
│   │   ├── previous_2.png
│   │   ├── previous_3.png
│   │   ├── previous_4.png
│   │   ├── previous_5.png
│   │   ├── previous_6.png
│   │   ├── previous_7.png
│   │   ├── previous_8.png
│   │   └── previous_9.png
│   ├── Mail-Database/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── previous.png
│   │   │   └── previous_1.png
│   │   ├── MailCreate.md
│   │   └── MailSend.md
│   ├── Mail-Database.md
│   ├── Processing-Trade-Requests/
│   │   ├── DealerAnswerAsync.md
│   │   ├── DealerConfirmCreate.md
│   │   ├── DealerExecuteAsync.md
│   │   ├── DealerExecutionCreate.md
│   │   ├── DealerGetAsync.md
│   │   ├── DealerLockAsync.md
│   │   ├── DealerStart.md
│   │   ├── DealerStop.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── next_2.png
│   │       ├── next_3.png
│   │       ├── next_4.png
│   │       ├── next_5.png
│   │       ├── next_6.png
│   │       ├── next_7.png
│   │       ├── previous.png
│   │       ├── previous_1.png
│   │       ├── previous_2.png
│   │       ├── previous_3.png
│   │       ├── previous_4.png
│   │       ├── previous_5.png
│   │       └── previous_6.png
│   ├── Processing-Trade-Requests.md
│   ├── Quote-and-News-Feeds/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── next_5.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_4.png
│   │   │   └── previous_5.png
│   │   ├── SendBookDiffs.md
│   │   ├── SendBooks.md
│   │   ├── SendEconomicEvents.md
│   │   ├── SendNews.md
│   │   ├── SendTicks.md
│   │   └── SendTickStats.md
│   ├── Quote-and-News-Feeds.md
│   ├── Server/
│   │   ├── Connections.md
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   └── previous_4.png
│   │   ├── IP.md
│   │   ├── Port.md
│   │   ├── Start.md
│   │   └── Stop.md
│   ├── Server.md
│   ├── Synchronizing-Trading-Data/
│   │   ├── GatewayAccountAnswer.md
│   │   ├── GatewayAccountRequest.md
│   │   ├── GatewayAccountSet.md
│   │   └── images/
│   │       ├── next.png
│   │       ├── next_1.png
│   │       ├── next_2.png
│   │       ├── previous.png
│   │       ├── previous_1.png
│   │       └── previous_2.png
│   ├── Synchronizing-Trading-Data.md
│   ├── Tick-Data/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   └── previous_3.png
│   │   ├── TickHistoryAdd.md
│   │   ├── TickHistoryReplace.md
│   │   ├── TickHistoryRequest.md
│   │   └── TickHistoryRequestRaw.md
│   ├── Tick-Data.md
│   ├── Trade-Databases/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── previous.png
│   │   │   └── previous_1.png
│   │   ├── OrderCreate.md
│   │   └── PositionCreate.md
│   ├── Trade-Databases.md
│   ├── Trade-Requests/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── next_5.png
│   │   │   ├── next_6.png
│   │   │   ├── next_7.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_4.png
│   │   │   ├── previous_5.png
│   │   │   ├── previous_6.png
│   │   │   └── previous_7.png
│   │   ├── RequestArrayCreate.md
│   │   ├── RequestCreate.md
│   │   ├── RequestGet.md
│   │   ├── RequestGetAll.md
│   │   ├── RequestNext.md
│   │   ├── RequestSubscribe.md
│   │   ├── RequestTotal.md
│   │   └── RequestUnsubscribe.md
│   ├── Trade-Requests.md
│   ├── User-Settings/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── next_5.png
│   │   │   ├── next_6.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_4.png
│   │   │   └── previous_5.png
│   │   ├── SettingsAdd.md
│   │   ├── SettingsClear.md
│   │   ├── SettingsDelete.md
│   │   ├── SettingsGet.md
│   │   ├── SettingsNext.md
│   │   ├── SettingsTotal.md
│   │   └── SettingsUpdate.md
│   ├── User-Settings.md
│   ├── Users/
│   │   ├── images/
│   │   │   ├── next.png
│   │   │   ├── next_1.png
│   │   │   ├── next_2.png
│   │   │   ├── next_3.png
│   │   │   ├── next_4.png
│   │   │   ├── next_5.png
│   │   │   ├── next_6.png
│   │   │   ├── next_7.png
│   │   │   ├── next_8.png
│   │   │   ├── previous.png
│   │   │   ├── previous_1.png
│   │   │   ├── previous_2.png
│   │   │   ├── previous_3.png
│   │   │   ├── previous_4.png
│   │   │   ├── previous_5.png
│   │   │   ├── previous_6.png
│   │   │   ├── previous_7.png
│   │   │   └── previous_8.png
│   │   ├── UserCreate.md
│   │   ├── UserCreateAccount.md
│   │   ├── UserGet.md
│   │   ├── UserGetByAccount.md
│   │   ├── UserGroup.md
│   │   ├── UserLogins.md
│   │   ├── UserSubscribe.md
│   │   ├── UserTotal.md
│   │   └── UserUnsubscribe.md
│   └── Users.md
├── Main-Interface.md
├── NET-Implementation.md
├── README.md
├── Symbol-and-Price-Translation.md
└── Trade-Operations-in.md
```

---

## 📄 Files

<a id='cmtgatewayapifactory-md'></a>
### 195. `CMTGatewayAPIFactory.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / CMTGatewayAPIFactory

[Previous](Exported-Functions/MTGatewayCreateLocal.md) | [Next](CMTGatewayAPIFactory/Initialize.md)

# CMTGatewayAPIFactory

The interfaces factory is provided in the "MT5APIateway.h" file to ease the access to the IMTGatewayAPI interface. This factory automatically downloads a necessary GatewayAPI library (32/64-bit) and gives access to the [exported functions](Exported-Functions.md).

The factory contains the following methods:

Method | Description  
---|---  
[Initialize](CMTGatewayAPIFactory/Initialize.md) | Loading of Gateway API library and all functions exported by it.  
[Shutdown](CMTGatewayAPIFactory/Shutdown.md) | Gateway API library unloading.  
[Create](CMTGatewayAPIFactory/Create.md) | Create an instance of the [IMTGatewayAPI](Main-Interface.md) interface.  
[LicenseCheck](CMTGatewayAPIFactory/LicenseCheck.md) | Gateway/data feed module usage license verification.  
[Version](CMTGatewayAPIFactory/Version.md) | Get the version of the loaded Gateway API library.  
  
Using factories in application development is optional. You can use your own implementation of corresponding functions.

```

---

<a id='development-and-debugging-of-gateways-md'></a>
### 195. `Development-and-Debugging-of-Gateways.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Development and Debugging of Gateways

[Previous](Trade-Operations-in.md) | [Next](Symbol-and-Price-Translation.md)

<a id="developing-and-debugging-gateways"></a>
# Developing and Debugging Gateways (#developing-and-debugging-gateways)

One of the major advantages of MetaTrader 5 is its ability of complete integration with other trading systems. MetaTrader 5 integration is performed using the special library - Gateway API.

Using Gateway API, application developers can easily create their source of quotes and news or a gateway to an external trading system.

The section thoroughly describes basic principles of developing and debugging gateways, as well as the working example of "SampleGateway" in C++. Development of data feeds using Gateway API is described in details in the section ["Developing Data Feeds"](Development-of-Data-Feeds.md).

<a id="gateways-operation-principles-in-metatrader-5"></a>
## Gateways Operation Principles in MetaTrader 5 (#gateways-operation-principles-in-metatrader-5)

Gateways are executable files (*.exe) launched as separate processes. All gateways modules are reentrant. This means that several gateways can be created using one gateway *.exe module.

The main difference of gateways from data feeds is the ability to perform trading operations on the part of MetaTrader 5 platform in an external trading system. Besides, gateways allow to transfer quotes and news to MetaTrader 5 platform, similar to data feeds.

Any gateway may be launched automatically by a history server or work remotely. To allow a history server to launch a gateway, its executable file must be copied to gateway\<gateway name> subdirectory of the history server directory (for example, gateway\SampleGateway). This directory is the working directory of the gateway. All gateway data, operation logs, temporary parameters, etc. will be stored here. The value corresponding to a gateway name should be used as a gateway module, while performing settings in the administrator terminal.

To let the gateway work remotely, it must be launched with correct [command line parameters (#param)](Exported-Functions/MTGatewayCreateLocal.md#param). ["Remote Gateway"](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_gateways/gateway_service) value should be used as a gateway module, while setting up the gateway in the administrator terminal. This mode is also used for debugging gateways during their development.

After it has been launched, the gateway opens the server port to receive connections of MT5 platform distributed components. Components connection process is strictly defined and described in "[Interaction of the Platform and Gateway API](Interaction-of-the-Platform-and.md)".

Connection of a history server to the gateway is the first one to be established. It is used to deliver the appropriate parameters to the gateway and getting a stream of quotes and operation logs from it.

Connection of the main trading server to the gateway is the second one to be established. It is used to deliver the platform settings, trading symbols, groups and trading parameters to the gateway. Connection of other trading servers is established only after the main trading server has been connected. Any connection of a trading server (the main or secondary one) is used by the gateway to perform trading operations. After the connection to the main trading server has been established, the gateway is ready for operation with MetaTrader 5 platform.

After the gateway has been completely synchronized with MT5 platform, it can start performing its basic functions - transferring trading symbols, quotes, trading requests, etc. Connection to an external trading system must be established for that. Various exchanges, ECNs, etc. can serve as a trading system.

![How the Gateway Works](images/sample_gateway_scheme.png)

<a id="description-of-metatrader-5-gateway-api-for-working-with-the-gateway"></a>
## Description of MetaTrader 5 Gateway API for Working with the Gateway (#description-of-metatrader-5-gateway-api-for-working-with-the-gateway)

In this article we consider only the features of interaction with Gateway API when creating gateways. Development of data feeds has been described in a [separate section](Development-of-Data-Feeds.md).

After initializing the application and all Gateway API interfaces, it starts accepting incoming connections of MetaTrader 5 platform servers. After connecting the history and the main trading server, the gateway application is notified of the successful initial synchronization with MetaTrader 5 platform. The notification is performed by calling [IMTGatewayAPISink::OnGatewayStart](Event-Interface/OnGatewayStart.md) interface method.

This call allows the application to call data processing methods - trading symbols synchronization with an external system, submission of quote data, handling clients' trading requests, synchronization of an external system quotes with the ones in MT5, etc.

Symbols are imported to MetaTrader 5 platform during the initial synchronization or when updating data on them. IMTGatewayAPI interface methods are used for importing trading symbols to Gateway API:

  * [SymbolCreate](Main-Interface/Configuration-Databases/Symbols/SymbolCreate.md) \- creating a trading symbol settings interface.
  * [SymbolAddPreliminary](Main-Interface/Configuration-Databases/Symbols/SymbolAddPreliminary.md) \- synchronous dispatch of a trading symbol settings to MetaTrader 5 platform. All newly added trading symbols are put to the "\Preliminary" symbols subgroup with trading function being disabled. To perform trading operations with the symbol, an administrator should relocate it to the necessary group and allow trading.



If the symbol is already present in MetaTrader 5 platform, calling the method for adding a trading symbol will update parameters of the existing symbol without changing the path in the group. The filled copy of IMTConSymbol interface created as a result of calling [IMTGatewatAPI::SymbolCreate](Main-Interface/Configuration-Databases/Symbols/SymbolCreate.md) is submitted to this method as a parameter.

The gateway performs trading operations as a dealer connecting to the trading requests queue, picking a request for processing and confirming by processing result. The main difference of Gateway API from a conventional dealer is that all trading servers are connected to Gateway API and a unified requests queue is generated from requests queues belonging to each definite server. To manage the requests queue, IMTGatewayAPI interface methods are used in Gateway API:

  * [DealerStart](Main-Interface/Processing-Trade-Requests/DealerStart.md) \- connecting the gateway to the trading platform as a dealer. Using flags parameter allows to connect the queue with automatic picking of incoming trading requests and get additional request data concerning a client, an order, a position and a trading account. As the use of additional request data reduces MetaTrader 5 productivity, it should be applied only in exceptional cases.
  * [DealerStop](Main-Interface/Processing-Trade-Requests/DealerStop.md) \- disconnecting the gateway from the requests queue. After disconnecting from the requests queue as a dealer, the gateway application no longer gets the queue updates.
  * [DealerLockAsync](Main-Interface/Processing-Trade-Requests/DealerLockAsync.md) \- picking a request from the requests queue by ID. ID of the request that should be picked is submitted to this method as a parameter. This value can be obtained by [IMTRequest::ID](../Database-Interfaces/Trade/Trade-Requests/IMTRequest/Requests-ID.md) method. The request that has been picked by successful execution of this method, returns in [IMTGatewaySink::OnDealerLock](Event-Interface/OnDealerLock.md) method.
  * [DealerAnswerAsync](Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md) \- confirmation of the request that has been previously picked from the queue. The pointer to IMTConfirm request confirmation object containing the request ID, confirmation code, etc. is submitted to this method as a parameter.



Notification of the application of the results of requests and confirmations processing is performed by calling virtual IMTGatewaySink [IMTGatewaySink](Event-Interface.md) methods:

  * [OnDealerLock](Event-Interface/OnDealerLock.md) \- the gateway application notification on the result of picking a request for processing. If a request is picked successfully, MT_RET_OK value will be transferred in retcode value, otherwise - an error code. A trading request description is transmitted in request parameter.
  * [OnDealerAnswer](Event-Interface/OnDealerAnswer.md) \- the gateway application notification of the request confirmation processing result. If the trading request confirmation is processed successfully, MT_RET_OK value will be transferred in retcode value, otherwise - an error code. A trading request confirmation description is transmitted in 'confirm' parameter.
  * [HookGatewayAccountRequest](Event-Interface/HookGatewayAccountRequest.md) \- the hook for synchronizing MetaTrader 5 client's trading data with an external trading system. The hook is called when clicking "Synchronize" at "Account" tab of MetaTrader 5 Administrator, as well as when calling IMTAdminAPI::UserExternalSync and IMTManagerAPI::UserExternalSync methods from MetaTrader 5 Manager API. To synchronize the trading data, pass it to the platform using the [IMTGatewayAPI::GatewayAccountAnswer](Main-Interface/Synchronizing-Trading-Data/GatewayAccountAnswer.md) method.
  * [HookGatewayPositionsRequest](Event-Interface/HookGatewayPositionsRequest.md) \- the hook for receiving states of trading accounts used by the gateway to operate in an external system. The hook is called when clicking "Request" on "Positions" tab of the gateway in MetaTrader 5 Administrator. Set the [MTGatewayInfo::GATEWAY_MODE_POSITIONS](../Structures/MTGatewayInfo.md) flag during the gateway initialization to inform the platform of the possibility to request the states of positions. The states of positions are sent to the platform using the [IMTGatewayAPI::GatewayPositionsAnswer](Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md) method.



  * The account in an external trading system should be specified in the account settings ("Account" tab) to request a trading data from that system.
  * After receiving a request for the account trading data synchronization or all accounts' position states, the gateway is to gather these data (for example, by sending a request to an external system) and pass them to MetaTrader 5 within 10 seconds (request lifetime).

  
---  
  
<a id="representation"></a>
## Gateway presentation to users: logo and description (#representation)

MetaTrader 5 supports the loading of the gateway logo and description from resources. Use this option to present your product in the [gateway showcase in MetaTrader 5 Administrator](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_gateways), as well as to provide documentation on the spot.

![Gateway presentation in MetaTrader 5 Administrator](images/gateway_showcase.png)

Add resources with the "DESCRIPTION" type and with the following IDs to your project:

  * 1000 — module description in free form, in UTF-8 format. Use an HTML document without classes and style, only with simple tags: h3, p, ul, ol, b, i. Standard Administrator terminal styles will be applied to the description and it will naturally fit into the interface.
  * 1001 — square logo for the showcase.
  * 1002 — square logo for high-resolution monitors.
  * 1003 — rectangle logo for the list of gateways and the details page.
  * 1004 — rectangle logo for high-resolution monitors.



An example of a .RC project file block:
    
    
    1000 DESCRIPTION "res\\description.html"
    1001 DESCRIPTION "res\\200x200.png"
    1002 DESCRIPTION "res\\400x400.png"
    1003 DESCRIPTION "res\\360x100.png"
    1004 DESCRIPTION "res\\720x200.png"

When loading the gateway module, the history server will pass this data to the main server, from which the information will be displayed in MetaTrader 5 Administrator.

<a id="processing-of-trading-requests-by-the-gateway"></a>
## Processing of Trading Requests by the Gateway (#processing-of-trading-requests-by-the-gateway)

There are two ways to process clients' market requests by the gateway. They can be conventionally called synchronous and asynchronous ones. They have similar procedures of getting a request by a server, its verification and routing in a requests queue. Vital differences begin at the point of processing a request.

During the synchronous processing of trading requests the gateway processes a customer's request, executes necessary operations (for example, transfers the request to an external system) and returns the result of its processing ([IMTConfirm](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTConfirm.md) request confirmation) to MT5 platform within the request lifetime (3 minutes). All necessary data (including the order tick in an external system, price and volume, etc.) has already been filled in confirmation of the request. Therefore, the client terminal gets data on a specific result of a request execution together with confirmation of the request execution.

The main limitations of this mechanism are:

  * Time of requests execution in an external trading system - an external system may not guarantee request execution time suitable for MetaTrader 5.
  * External trading system architecture - it is difficult to clearly associate the requests with their processing results. For example, asynchronous notification of the operations results, the ability to change orders and deals status from an external system, partial execution, etc.
  * Trading request setting delay - an objective need to provide a trader with the possibility to set the maximum number of requests in the minimum amount of time.



Considering these limitations, we can say that this mechanism is suitable for trading systems of market-maker markets having high (almost 100%) liquidity and guaranteed execution time suitable for MetaTrader 5.

If one of these conditions is violated (for example, there are partial executions for exchanges and ECNs with undetermined market order execution time and the operation of a trading system is strictly asynchronous), the gateway sends only synchronous confirmation of transferring a trading request to an external trading system. All other actions are determined only by the system productivity.

Notification of MetaTrader 5 platform is performed asynchronously via a stream of trading executions using [IMTExecution](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTExecution.md) interface. This mode is an asynchronous way to process trading requests. The mechanism is optimized for order-driven trading systems - exchanges and ECNs having high demands for productivity and unguaranteed execution time.

In the example of the gateway considered in this article we describe the operation of the gateway only in synchronous mode.

<a id="the-gateway-structure"></a>
## The Gateway Structure (#the-gateway-structure)

From a technical point of view, the main task of the gateway is to arrange data exchange between two different trading systems: MetaTrader 5 and an external one. Each system submits its own interaction interface. Interaction with MetaTrader 5 trading platform is located in two Gateway API interfaces: [IMTGatewayAPI](Main-Interface.md) and [IMTGatewayAPISink](Event-Interface.md). Interaction with an external system is arranged using API submitted by an external system provider.

Basic application class (CMTGatewayApp in our case) is an entry point of the gateway application. It implements launch/stop operations of the application and all of its major work. The class is inherited from [IMTGatewaySink](Event-Interface.md) interface. Its objectives are initialization, connection to/disconnection from Gateway API, getting notifications from MT5 platform about various events taking place in it and submitting them to the gateway class (CGateway in our case).

The gateway class implements its business logic and provides interaction of MT5 platform with an external trading system. In fact, the class assigns implementation of the gateway business logic to its subclasses.

To provide interaction of the gateway with MetaTrader 5 platform, the gateway class refers to [IMTGatewayAPI](Main-Interface.md) interface. To provide interaction of the gateway with an external trading system, the gateway class refers to the interface of the interaction with an external trading system (CExchangeAPI in our case).

To process MetaTrader 5 event notifications concerning trading requests (for example, picking a trading request from the requests queue, result of request confirmation by MT5 platform), the gateway class refers to trading dispatcher class (CTradeDispatcher in the example). The objectives of this class are as follows:

  * receiving, analyzing and processing of clients' trading requests;
  * transferring trading requests to an external trading system;
  * generation of trading requests and trading executions confirmations;
  * processing of external trading system responses to trading requests.



The interface class of interaction with an external trading system implements two basic functions: storing data on trading symbols and logic of processing and data exchange between MT5 platform and an external trading system. This data includes trading symbols settings, quotes data, trading requests etc. The class assigns these functions to its subclasses - the class of available trading symbols base (CExchangeSymbols in the example) and the class of the context of connection to an external trading system (CExchangeContext in the example).

The class of available trading symbols base is used for storing data on trading symbols and synchronization of trading symbols settings with the ones in MetaTrader 5 platform. This class provides adding, changing, deleting, searching available trading symbols and processing all transactions received from an external trading system and related to the trading symbols. Such transactions are, for example, getting trading symbols settings, quotes data, responses to trading requests from an external trading system etc.

Let's consider the process of data exchange between the gateway and an external trading system. Generally, the data exchange occurs in several stages:

  * Data conversion from MetaTrader 5 platform format to an external trading system one (and vice versa);
  * Data package generation/unpacking according to the established protocol of data exchange with external trading system;
  * Exchanging data packages with an external trading system server.



Data exchange between the gateway and an external system is performed in the external connection context class. Generally, the gateway may have several contexts of connection to an external trading system. This class is designed to receive/send data packages between an external trading system and the gateway. Data packages are generated according to the exchange protocol (CExchangeProtocol class in our case), submitted by an external system provider.

The connection context class refers to a special class providing an appropriate functionality (CExchangeSocket in our case) to physically connect to an external trading system server and receive/send data packages. Its implementation is fully determined by the type of an external connection delivered by an external system provider.

<a id="samplegateway"></a>
## SampleGateway (#samplegateway)

Ready-made working example will allow programmers to quickly and efficiently implement their own applications for integration with MetaTrader 5 based on Gateway API. To achieve this, we have developed the example of SampleGateway that may serve as a template when developing a custom application.

SampleGateway (similar to SampleExchange external trading system described below) is a 32/64-bit application developed in C++ in Microsoft Visual Studio 2005/2008 environment. Free Express versions of MS Visual Studio can be [downloaded from Microsoft website](https://www.microsoft.com/express/Downloads/).

Simplified gateway module has been implemented in SampleGateway. The gateway connects to MetaTrader 5 via Gateway API. After the full synchronization with the platform, the gateway initiates connection to SampleExchange external trading system (described below) via the appropriate interface. Further on, the gateway receives the settings of all trading symbols available in an external trading system.

Four trading symbols with various orders execution modes are available to be displayed in an external trading system:

  * "EURUSD.TEST" having request execution mode;
  * "GBPUSD.TEST" having instant execution mode;
  * "USDCHF.TEST" having market execution mode;
  * "MQ-FUT" having exchange execution mode.



After the gateway gets all symbols, connection of the gateway and an external trading system is deemed to be synchronized. Since that moment, the gateway starts getting quotes data on all available trading symbols from an external trading system. Besides, the gateway connects to the trading requests queue and starts processing them.

> SampleGateway is a demo gateway interacting only with SampleExchange external trading system.

Let us have a more detailed look at SampleGateway structure including the source code.

<a id="samplegateway-initialization-and-launch"></a>
## SampleGateway Initialization and Launch (#samplegateway-initialization-and-launch)

We will start from implementation of CMTGatewayApp application basic class. As it has already been noted, it is inherited from IMTGatewaySink interface. The first thing to do is to initialize Gateway API factory classes using [CMTGatewayAPIFactory::Initialize](CMTGatewayAPIFactory/Initialize.md) method and create a copy of Gateway API using [CMTGatewayAPIFactory::Create](CMTGatewayAPIFactory/Create.md) method:
    
    
    //--- initialize Gateway API library
       if(m_api_factory.Initialize()!=MT_RET_OK)
          return(false);
    //--- generate description
       Info(info);
    //--- create Gateway API instance
       res=m_api_factory.Create(info,&m_api_gateway,argc,argv);

The first parameter of [CMTGatewayAPIFactory::Create](CMTGatewayAPIFactory/Create.md) method receives description of the gateway module as the structure of [MTGatewayInfo](../Structures/MTGatewayInfo.md). This structure must first be filled This is performed in CMTGatewayApp::Info: method in our case:
    
    
    void CMTGatewayApp::Info(MTGatewayInfo &info)
      {
    //--- generate description
       ZeroMemory(&info,sizeof(info));
    //--- data
       info.version    =ProgramBuild;
       info.version_api=MTGatewayAPIVersion;
       CMTStr::Copy(info.name_default,      _countof(info.name_default),ProgramName);
       CMTStr::Copy(info.copyright,         _countof(info.copyright),         L"Copyright 2001-2016, MetaQuotes Software Corp.");
       CMTStr::Copy(info.build_date,        _countof(info.build_date),        ProgramBuildDate);
       CMTStr::Copy(info.build_api_date,    _countof(info.build_api_date),    MTGatewayAPIDate);
       CMTStr::Copy(info.server_default,    _countof(info.server_default),    L"127.0.0.1");
       CMTStr::Copy(info.login_default,     _countof(info.login_default),     L"default");
       CMTStr::Copy(info.password_default,  _countof(info.password_default),  L"default");
       CMTStr::Copy(info.module_id,         _countof(info.module_id),         L"gatewayid");
       info.mode  =MTGatewayInfo::GATEWAY_MODE_QUOTES|MTGatewayInfo::GATEWAY_MODE_POSITIONS;
       info.fields=MTGatewayInfo::GATEWAY_FIELD_ALL;
       CMTStr::Copy(info.description,       _countof(info.description)-1,ProgramDescription);
      }

The gateway life cycle is implemented in CMTGatewayApp::Run method: launch of Gateway API server port, the gateway running cycle and turning Gateway API server port off after completing the operation:
    
    
    bool CMTGatewayApp::Run()
      {
    //--- ...
    //--- start Gateway API
       if(m_api_gateway->Start(this)!=MT_RET_OK)
         {
          ExtLogger.Out(MTLogErr,L"MTGatewayApp: failed to start MetaTrader 5 Gateway API");
          return(false);
         }
    //--- set working flag
       Working(1);
    //---- main loop of check
       while(Working())
         {
          //--- check gateway state
          m_gateway->Check();
          //--- sleep
          Sleep(TIMEOUT_CHECK_STATE);
         }
    //--- stop Gateway API
       m_api_gateway->Stop();
    //--- ...
      }

[IMTGatewayAPI::Start](Main-Interface/Server/Start.md) method called in this code launches Gateway API server port. After that, the application flow is transferred to a working state using Working(1) method. Method [IMTGatewayAPI::Stop](Main-Interface/Server/Stop.md) is used to turn Gateway API server port off.

<a id="samplegateway-interaction-with-an-external-trading-system"></a>
## SampleGateway Interaction with an External Trading System (#samplegateway-interaction-with-an-external-trading-system)

In the above example m_gateway is a pointer to CGateway class. According to the gateway and external connection states, calling m_gateway->Check method manages application flows - the flows of transactions processing and data exchange with an external trading system:
    
    
    void CGateway::Check(void)
      {
    //--- check
       if(!m_api_exchange)
          return;
    //--- exit if Gateway API is not ready for work
       if(StatusGateway()<=STATUS_API_CONFIGURED)
          return;
    //--- API is ready for work, check connection to external trading system
       if(StatusExchange()>=STATUS_CONNECTED)
         {
          //--- check connection to external trading system
          if(!m_api_exchange->Check())
            {
             //--- external trading system haven't responded during timeout
             ExtLogger.Out(MTLogErr,L"exchange timed out");
             StatusExchange(STATUS_DISCONNECTED);
             return;
            }
         }
    //--- analyze state, start connection in the check thread,
    //--- it is safe, because external trading system API is operating asynchronously
       if(StatusExchange()<=STATUS_CONNECTING)
          Connect();
      }

CGateway::Connect method calling is asynchronous one. It initializes the interface of the interaction with an external trading system and the launch of its workflow. Let us consider the interface of interaction with an external trading system in details.

The interface of interaction with an external trading system has been implemented in CExchangeAPI class. Processing of the data obtained in connection contexts is arranged in a separate flow. This allows to improve the performance of the gateway application, separate the process of the network input/output and processing the data obtained from an external trading system.

Processing of accumulated transactions received from an external trading system is performed in the workflow of the interface for interaction with CExchangeAPI external trading system:
    
    
    void CExchangeAPI::ProcessThread(void)
     
      {
       bool trans_applied=false;
    //--- loop of data processing
       while(InterlockedExchangeAdd(&m_thread_workflag,0)>0)
         {
          //--- process received data
          m_exchange_context.TransApply(m_symbols,trans_applied);
          //--- sleep if there are no transactions
          if(!trans_applied)
             Sleep(TRANS_WAIT_TIME);
         }
      }

<a id="samplegateway-connection-to-an-external-trading-system"></a>
## SampleGateway Connection to an External Trading System (#samplegateway-connection-to-an-external-trading-system)

CExchangeContext is the context class of the external connection in this example. As noted above, the gateway may have several connection contexts according to the number of various connections to an external trading system. Only one external connection and, as a result, one context are used in SampleGateway application.

One more flow (connection context workflow) is launched during this class initialization. The main objective of the connection context class is a network data packages exchanges between the gateway and an external system in the connection context workflow.

Let us consider the workflow of an external connection context class:
    
    
    void CExchangeContext::ProcessThread(void)
      {
    //--- ...
    //--- initialize connection
       if(!m_socket->Connect(m_address,m_port))
          return;
    //--- flags of data processing
       bool data_send=false,data_receive=false;
    //--- loop of managing external connection
       while(InterlockedExchangeAdd(&m_thread_workflag,0)>0)
         {
          //--- receive sent data
          if(!ReceiveCheck(data_receive))
             break;
          //--- process data for sending
          if(!SendCheck(data_send))
             break;
          //--- if there was no data exchange, then sleep
          if(!data_send && !data_receive)
             Sleep(THREAD_SLEEP);
         }
    //--- close socket
       m_socket->Close();
    //--- ...
      }

The attempt to connect to an external trading system is made in this flow by calling m_socket->Connect method. Here m_socket is a pointer to CExchangeSocket class object implementing the functions of physical connection to/disconnection from an external trading system server, as well as data exchange with it.

Packages exchange between the gateway and an external trading system is implemented in ReceiveCheck and SendCheck methods of a basic cycle of that flow.

We will examine the code of the external connection context workflow.

After receiving the data packages, the context class unpacks a data packet using the data exchange protocol class. Depending on the data package type, it adds an appropriate transaction for processing by the class of the interface for interaction with CExchangeAPI external system. Let us display the implementation of the quotes data package processing method, in which a transaction with quotes data is added to m_trans_ticks ticks transactions array:
    
    
    bool CExchangeContext::OnMessageTick(const ExchangeMsgTick &msg)
      {
       bool res=false;
    //--- lock
       m_trans_sync.Lock();
    //--- add tick transaction for processing
       res=m_trans_ticks.Add(&msg.tick);
    //--- unlock
       m_trans_sync.Unlock();
    //--- return result
       return(res);
      }

Direct processing of obtained data is not included into the connection context class function. As mentioned above, it is performed in CExchangeAPI class flow in CExchangeContext::TransApply method:
    
    
    bool CExchangeContext::TransApply(CExchangeSymbols &symbols,bool &trans_applied)
      {
       bool res=false;
    //--- results of processing transactions
       bool symbols_applied=false,ticks_applied=false,books_applied=false,orders_applied=false,deals_applied=false;
    //--- clear arrays
       m_trans_symbols_tmp.Clear();
       m_trans_ticks_tmp.Clear();
       m_trans_books_tmp.Clear();
       m_trans_orders_tmp.Clear();
       m_trans_deals_tmp.Clear();
    //--- lock
       m_trans_sync.Lock();
    //--- get contents of arrays
       m_trans_symbols.Swap(m_trans_symbols_tmp);
       m_trans_ticks.Swap(m_trans_ticks_tmp);
       m_trans_books.Swap(m_trans_books_tmp);
       m_trans_orders.Swap(m_trans_orders_tmp);
       m_trans_deals.Swap(m_trans_deals_tmp);
    //--- unlock
       m_trans_sync.Unlock();
    //--- process received transactions
       res=TransApplySymbols(symbols,m_trans_symbols_tmp,symbols_applied);
       res=res && TransApplyTicks(symbols,m_trans_ticks_tmp,ticks_applied);
       res=res && TransApplyBooks(symbols,m_trans_books_tmp,books_applied);
       res=res && TransApplyOrders(symbols,m_trans_orders_tmp,orders_applied);
       res=res && TransApplyDeals(symbols,m_trans_deals_tmp,deals_applied);
    //--- flag of data availability
       trans_applied=symbols_applied || ticks_applied || books_applied || orders_applied || deals_applied;
    //--- return result
       return(res);
      }

Five types of transactions are processed here:

  * transactions with trading symbols settings in CExchangeContext::TransApplySymbols method;
  * transactions with quote data in CExchangeContext::TransApplyTicks method;
  * transactions with trading orders in CExchangeContext::TransApplyOrders method;
  * transactions with performed deals in CExchangeContext::TransApplyDeals method;
  * transactions with the current state of depth of market in CExchangeContext::TransApplyBooks method.



<a id="processing-of-samplegateway-transactions-using-available-trading-symbols-base-class"></a>
## Processing of SampleGateway Transactions Using Available Trading Symbols Base Class (#processing-of-samplegateway-transactions-using-available-trading-symbols-base-class)

The interface class for interaction with CExchangeAPI external trading system directs CExchangeSymbols available trading symbols base class to process all transactions. We will examine the processing of data transactions on the example of transaction with quote data:
    
    
    bool CExchangeSymbols::OnSymbolTickApply(const ExchangeTick &exchange_tick)
      {
    //--- ...
    //--- import tick
       MTTick gateway_tick={0};
    //--- import symbol
       CMTStr::Copy(gateway_tick.symbol,_countof(gateway_tick.symbol),exchange_tick.symbol);
    //--- import price source
       CMTStr::Copy(gateway_tick.bank,_countof(gateway_tick.bank),exchange_tick.bank);
    //--- import bid price
       gateway_tick.bid   =exchange_tick.bid;
    //--- import ask price
       gateway_tick.ask   =exchange_tick.ask;
    //--- import last price
       gateway_tick.last  =exchange_tick.last;
    //--- import last deal volume
       gateway_tick.volume=exchange_tick.volume;
    //--- import datetime
       gateway_tick.datetime=exchange_tick.datetime;
    //--- send to Gateway API
       return(m_gateway.GatewayTickSend(gateway_tick));
      }

In this case the quote data is converted from an external trading system (ExchangeTick) in MetaTrader 5 ([MTTick](../Structures/MTTick.md)) platform format and sent to a history server. Sending is implemented in CExchangeSymbols::OnSymbolTickApply method.

Similar processing has been implemented for other exchange data - trading symbols settings, trading orders, etc. Simplified processing of data transaction has been implemented in SampleGateway. Developers need to add their implementation to the mentioned methods for processing data transactions in the real gateway application.

<a id="trading-requests-processing-in-samplegateway"></a>
## Trading Requests Processing in SampleGateway (#trading-requests-processing-in-samplegateway)

Now, let us consider the trading interaction between the gateway, MetaTrader 5 platform and an external trading system.

As mentioned above, external connection of the gateway gets into STATUS_SYNCHRONIZED state after it receives all trading symbols from an external trading system. The stage of trading interaction comes after that. To achieve it, the gateway must connect to MetaTrader 5 trading requests queue using [IMTGatewayAPI::DealerStart](Main-Interface/Processing-Trade-Requests/DealerStart.md) method.

In SampleGateway this has been implemented in establishing CGateway::StatusExchange gateway external connection status method:
    
    
    LONG CGateway::StatusExchange(const LONG status)
      {
    //--- ...
       if(status==STATUS_SYNCHRONIZED)
         {
          //--- connect to the request queue
          m_api_gateway->DealerStart(IMTGatewayAPI::DEALER_FLAG_AUTOLOCK);
         }
    //--- ...
      }

After the gateway has connected to the queue of trading requests, they are picked by Gateway API and transferred to the gateway. At the same time Gateway API calls CMTGatewayApp::OnDealerLock notification method. The basic class of the application transfers a trading request to the gateway class, while this class, in its turn, transfers it to the trading dispatcher class.

The trading dispatcher has been implemented in CTradeDispatcher class of SampleGateway. The main function of the class is processing trading requests received from MetaTrader 5 platform, their confirmation and sending to an external trading system.

Trading requests processing has been implemented in CTradeDispatcher::GatewayProcess trading dispatcher class method. As SampleGateway is a simplified gateway sample, trading requests processing has been implemented only for demonstration purposes in this application.

After the gateway gets a trading request, the presence of a trade instrument, for which the request ([IMTRequest](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequest.md)) has arrived, is checked. Possibility of automatic confirmation is also checked. If the automatic confirmation is impossible, the request is sent to an external trading system in GatewayExecuteExchange method. 
    
    
    void CTradeDispatcher::GatewayProcess(const IMTRequest *request)
      {
    //--- ...
    //--- symbol
       ExchangeSymbol symbol={0};
    //--- check the presence of a symbol a request is assigned to
       if(!m_api_exchange->SymbolGet(request->Symbol(),symbol))
         {
          ExtLogger.Out(MTLogErr,L"symbol %s not found",request->Symbol());
          //--- send request error
          SendRequestConfirm(MT_RET_REQUEST_ERROR,request);
          return;
         }
    //--- check if a request can be confirmed automatically
       if(GatewayProcessAuto(request))
         {
          //--- confirm request
          SendRequestConfirm(MT_RET_REQUEST_DONE,request);
          return;
         }
    //--- execute request at an exchange
       if(!GatewayExecuteExchange(request))
         {
          //--- unable to send request to external system, send request error
          SendRequestConfirm(MT_RET_REQUEST_ERROR,request);
         }
      }

In GatewayExecuteExchange method, the request is converted in external trading system format (ExchangeOrder) and sent to it in m_api_exchange->SendOrder method:
    
    
    bool CTradeDispatcher::GatewayExecuteExchange(const IMTRequest *request)
      {
    //--- check
       if(!m_api_exchange)
          return(false);
    //--- send order
       ExchangeOrder exchange_order={0};
    //--- order action type
       UINT request_action=request->Action();
    //--- enter the type of operation
       GetOrderActionByRequestAction(request_action,exchange_order.order_action);
    //--- order ticket
       exchange_order.order_mt_id=request->Order();
    //--- order id in external system
       exchange_order.request_mt_id=request->ID();
    //--- symbol
       CMTStr::Copy(exchange_order.symbol,_countof(exchange_order.symbol),request->Symbol());
    //--- client's login
       exchange_order.login=request->Login();
    //--- order type
       exchange_order.type_order=request->Type();
    //--- expiration type
       exchange_order.type_time=request->TypeTime();
    //--- action
       exchange_order.action=request_action;
    //--- price
       exchange_order.price_order=request->PriceOrder();
    //--- Stop Loss level
       exchange_order.price_SL=request->PriceSL();
    //--- Take Profit level
       exchange_order.price_TP=request->PriceTP();
    //--- volume
       exchange_order.volume=UINT64(SMTMath::VolumeToDouble(request->Volume()));
    //--- expiration time
       exchange_order.expiration_time=request->TimeExpiration();
    //--- if Take Profit activation order arrived
       if(exchange_order.action==IMTRequest::TA_ACTIVATE_TP)
         {
          //--- send pending order
          exchange_order.action=IMTRequest::TA_PENDING;
          //--- order expires in 5 seconds
          exchange_order.expiration_time=GetExchangeTime()+MT_ORDER_ACTIVATION_TIMEOUT;
         }
    //--- if Stop Loss or Stop order activation order arrived
       if(exchange_order.action==IMTRequest::TA_ACTIVATE_SL || exchange_order.action==IMTRequest::TA_ACTIVATE)
         {
          //---  order activated on MT side
          if(exchange_order.action==IMTRequest::TA_ACTIVATE)
             exchange_order.order_custom_data=MT_ORDER_ACTIVATION_FLAG;
          //--- send market order
          exchange_order.action=IMTRequest::TA_EXCHANGE;
          //--- reset order price
          exchange_order.price_order=0;
          //--- order expires in 5 seconds
          exchange_order.expiration_time=GetExchangeTime()+MT_ORDER_ACTIVATION_TIMEOUT;
         }
    //--- if Stop Limit order activation order arrived
       if(exchange_order.action==IMTRequest::TA_ACTIVATE_STOPLIMIT)
         {
          //--- send pending order
          exchange_order.action=IMTRequest::TA_PENDING;
          //--- set order activation price
          exchange_order.price_order=request->PriceTrigger();
         }
    //--- send order to exchange
       return(m_api_exchange->SendOrder(exchange_order));
      }

On arrival of trading transaction from an external trading system, it is processed in CTradeDispatcher::OnExchangeOrderTrans trading dispatcher class method:
    
    
    bool CTradeDispatcher::OnExchangeOrderTrans(const ExchangeOrder &exchange_order,const ExchangeSymbol &symbol)
      {
       bool res=true;
    //--- analyze order state
       switch(exchange_order.order_state)
         {
          case ExchangeOrder::ORDER_STATE_CONFIRMED:
            {
             //--- send confirmation only
             res=res && SendOrderConfirm(exchange_order);
             break;
            }
          case ExchangeOrder::ORDER_STATE_REQUEST_PLACED:
          case ExchangeOrder::ORDER_STATE_REQUEST_MODIFY:
          case ExchangeOrder::ORDER_STATE_REQUEST_CANCEL:
            {
             //--- send confirmation and execution
             res=res && SendOrderConfirm(exchange_order);
             res=res && SendOrderExecution(exchange_order);
             break;
            }
          case ExchangeOrder::ORDER_STATE_NEW:
          case ExchangeOrder::ORDER_STATE_MODIFY:
          case ExchangeOrder::ORDER_STATE_CANCEL:
          case ExchangeOrder::ORDER_STATE_REJECT_NEW:
          case ExchangeOrder::ORDER_STATE_REJECT_MODIFY:
          case ExchangeOrder::ORDER_STATE_REJECT_CANCEL:
            {
             //--- send execution only
             res=res && SendOrderExecution(exchange_order);
             break;
            }
          default:
            {
             res=false;
            }
         }
       return(res);
      }

When processing such type of transactions, the state of an arrived order is analyzed in CTradeDispatcher::OnExchangeOrderTrans method. Depending on the analysis results, confirmation of trade requests ([IMTConfirm](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTConfirm.md)) or result of trade orders execution ([IMTExecution](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTExecution.md)) is sent to MetaTrader 5 platform..

The trade request is confirmed in [IMTGatewayAPI::DealerAnswerAsync](Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md) method. It has been shown in CTradeDispatcher::SendRequestConfirm trading dispatcher method:
    
    
    bool CTradeDispatcher::SendRequestConfirm(const ExchangeOrder &exchange_order)
      {
    //--- ...
       res=m_confirm_exchange->Clear()==MT_RET_OK;
       res=res && (m_confirm_exchange->ID((UINT)exchange_order.external_id)==MT_RET_OK);
       res=res && (m_confirm_exchange->Volume(exchange_order.volume)==MT_RET_OK);
       res=res && (m_confirm_exchange->Price(exchange_order.price_order)==MT_RET_OK);
       res=res && (m_confirm_exchange->TickBid(exchange_order.price_tick_bid)==MT_RET_OK);
       res=res && (m_confirm_exchange->TickAsk(exchange_order.price_tick_ask)==MT_RET_OK);
       res=res && (m_confirm_exchange->Retcode(exchange_order.result)==MT_RET_OK);
    //--- send confirmation to MT5
       res=res && (m_api_gateway->DealerAnswerAsync(m_confirm_exchange)==MT_RET_OK);
    //--- return result
       return(res);
      }

Results of trade orders' execution are sent in [IMTGatewayAPI::DealerAnswerAsync](Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md) method. It has been shown in CTradeDispatcher::SendOrderConfirm method:
    
    
    bool CTradeDispatcher::SendOrderConfirm(const ExchangeOrder &exchange_order)
      {
    //--- ...   
    //--- set confirmation data
       res=m_confirm_exchange->Clear()==MT_RET_OK;
       res=res && (m_confirm_exchange->ID((UINT)exchange_order.request_mt_id)==MT_RET_OK);
       CMTStr::FormatStr(str,L"%I64u",exchange_order.order_exchange_id);
       res=res && (m_confirm_exchange->OrderID(str)==MT_RET_OK);
       res=res && (m_confirm_exchange->Volume(SMTMath::VolumeToInt(double(exchange_order.volume)))==MT_RET_OK);
       res=res && (m_confirm_exchange->Price(exchange_order.price_order)==MT_RET_OK);
       res=res && (m_confirm_exchange->TickBid(exchange_order.price_tick_bid)==MT_RET_OK);
       res=res && (m_confirm_exchange->TickAsk(exchange_order.price_tick_ask)==MT_RET_OK);
       res=res && (m_confirm_exchange->Retcode(exchange_order.result)==MT_RET_OK);
    //--- send confirmation to MT5
       if(res && m_api_gateway->DealerAnswerAsync(m_confirm_exchange)!=MT_RET_OK)
         {
          ExtLogger.Out(MTLogErr,L"'%I64u': request #%I64u failed to send confirm %s (%d)",
                        exchange_order.login,
                        exchange_order.order_exchange_id,
                        m_confirm_exchange->Print(str),
                        res);
          res=false;
         }
       else
          LogAnswerExchange(exchange_order,m_confirm_exchange);
    //--- return result
       return(res);
      }

<a id="samplegateway-trading-data-synchronization"></a>
## SampleGateway Trading Data Synchronization (#samplegateway-trading-data-synchronization)

If [an account in an external trading system (#trade-accounts)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_accounts/account_edit#trade-accounts) is specified for a trade account, then the [IMTGatewaySink::HookGatewayAccountRequest](Event-Interface/HookGatewayAccountRequest.md) hook is called when clicking "Synchronize" at "Account" tab of MetaTrader 5 Administrator, as well as when calling IMTAdminAPI::UserExternalSync and IMTManagerAPI::UserExternalSync methods from MetaTrader 5 Manager API. In SampleGateway, the request for client's trading data is passed to the gateway class.
    
    
    MTAPIRES CMTGatewayApp::HookGatewayAccountRequest(UINT64 login,LPCWSTR account_id)
      {
       MTAPIRES res=MT_RET_ERROR;
    //--- notify gateway
       if(m_gateway)
          res=m_gateway->HookGatewayAccountRequest(login,account_id);
    //--- return result
       return(res);
      }

The gateway sends an account trading data request to the external trading system using the m_api_exchange->SendAccountDataRequest method with a specified login.
    
    
    MTAPIRES CGateway::HookGatewayAccountRequest(UINT64 login,LPCWSTR account_id)
      {
       bool res;
    //--- request account data from exchange
       res=m_api_exchange->SendAccountDataRequest(login);
    //--- return result
       return(res?MT_RET_OK:MT_RET_ERROR);
      }

If the MTGatewayInfo::GATEWAY_MODE_POSITIONS flag has been specified in [MTGatewayInfo::mode](../Structures/MTGatewayInfo.md) when creating a GatewayAPI instance, the tab allowing you to request the [list of positions in an external system](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_gateways/gateway_positions) becomes available in the gateway page of the MetaTrader 5 Administrator. The [IMTGatewaySink::HookGatewayPositionsRequest](Event-Interface/HookGatewayPositionsRequest.md) hook is called during the request. In SampleGateway, the request for positions is passed to the gateway class.
    
    
    MTAPIRES CMTGatewayApp::HookGatewayPositionsRequest()
      {
       MTAPIRES res=MT_RET_ERROR;
    //--- notify gateway
       if(m_gateway)
          res=m_gateway->HookGatewayPositionsRequest();
    //--- return result
       return(res);
      }

In order to receive the list of all positions, the gateway sends a trading data request to the external trading system using the m_api_exchange->SendAccountDataRequest method with no login specified.
    
    
    MTAPIRES CGateway::HookGatewayPositionsRequest()
      {
       ExchangePositionsArray positions_exchange;
       IMTPositionArray   *positions_gateway=NULL;
       MTAPIRES            res              =MT_RET_OK;
    //--- get exchange positions
       if(!m_api_exchange->SendAccountDataRequest(0))
          res=MT_RET_ERROR;
    //--- return result
       return(res);
      }

When data from the external system arrive, they are processed using the CGateway::OnExchangeAccountDataReceived method.
    
    
    bool CGateway::OnExchangeAccountDataReceived(const ExchangeAccountData &account_data)
      {
       IMTUser            *user_gateway     =NULL;
       IMTAccount         *account_gateway  =NULL;
       IMTOrderArray      *orders_gateway   =NULL;
       IMTPositionArray   *positions_gateway=NULL;
       MTAPIRES            res              =MT_RET_OK;
    //--- create user interface
       user_gateway=m_api_gateway->UserCreate();
    //--- create account interface
       account_gateway=m_api_gateway->UserCreateAccount();
    //--- create positions array interface
       positions_gateway=m_api_gateway->GatewayPositionArrayCreate();
    //--- create orders array interface
       orders_gateway=m_api_gateway->GatewayOrderArrayCreate();
    //--- check interfaces
       if(!user_gateway || !account_gateway || !orders_gateway || !positions_gateway)
          res=MT_RET_ERR_MEM;
    //--- if login is specified 
       if(account_data.login>0)
         {
          //--- request user data 
          res=m_api_gateway->UserGet(account_data.login,user_gateway);
          //--- set account balance
          if(res==MT_RET_OK)
             res=account_gateway->Balance(account_data.balance);
         }
    //--- convert orders
       if(res==MT_RET_OK && account_data.orders.Total()>0)
          res=ConvertOrders(account_data.orders,orders_gateway);
    //--- convert positions
       if(res==MT_RET_OK && account_data.positions.Total()>0)
         {
          res=ConvertPositions(account_data.positions,positions_gateway);
         }
    //--- answer with data
       if(res==MT_RET_OK)
         {
          //--- if login is specified, answer in HookGatewayAccountRequest
          if(account_data.login)
             res=m_api_gateway->GatewayAccountAnswer(res,m_api_gateway->TimeCurrent(),user_gateway,account_gateway,orders_gateway,positions_gateway);
          else 
            {
             //--- answer in HookGatewayPositionsRequest
             res=m_api_gateway->GatewayPositionsAnswer(res,m_api_gateway->TimeCurrent(),positions_gateway);
            }
         }
    //--- release interfaces
       if(user_gateway)
          user_gateway->Release();
       if(account_gateway)  
          account_gateway->Release();
       if(orders_gateway)
          orders_gateway->Release();
       if(positions_gateway)
          positions_gateway->Release();
    //--- return result
       return(res==MT_RET_OK || res==MT_RET_OK_NONE);
      }

The interfaces of a user, a trade account, a list of orders and positions are created here. If a trading login is specified, its balance is displayed in the external system. The list of orders and positions is converted into MetaTrader 5 format. After that, the gateway responds to an initial hook using [IMTGatewayAPI::GatewayAccountAnswer](Main-Interface/Synchronizing-Trading-Data/GatewayAccountAnswer.md) or [IMTGatewayAPI::GatewayPositionsAnswer](Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md) method and releases the created interfaces.

Orders are converted using the CGateway::ConvertOrders method
    
    
    MTAPIRES CGateway::ConvertOrders(const ExchangeOrdersArray &exchange_orders,IMTOrderArray *gateway_orders) const
      {
       IMTOrder      *gateway_order=NULL;
       ExchangeSymbol exchange_symbol;
       CMTStr32       str;
       MTAPIRES       res          =MT_RET_OK;
    //--- check
       if(!m_api_gateway || !gateway_orders)
          return(false);
    //--- go through all orders
       for(UINT i=0;i<exchange_orders.Total() && res==MT_RET_OK;i++)
         {
          //--- skip empty orders
          if(exchange_orders[i].volume==0)
             continue;
          //--- get Gateway API order interface
          if((gateway_order=m_api_gateway->OrderCreate())!=NULL)
            {
             //--- set order ticket
             res=gateway_order->OrderSet(exchange_orders[i].order_mt_id);
             //--- format order external id
             str.Format(L"%I64u",exchange_orders[i].order_exchange_id);
             //--- set order external id
             if(res==MT_RET_OK)
                res=gateway_order->ExternalID(str.Str());
             //--- set order symbol
             if(res==MT_RET_OK)
                res=gateway_order->Symbol(exchange_orders[i].symbol);
             //--- set order volume
             if(res==MT_RET_OK)
                res=gateway_order->VolumeInitial(SMTMath::VolumeToInt((double)exchange_orders[i].volume));
             if(res==MT_RET_OK)
                res=gateway_order->VolumeCurrent(SMTMath::VolumeToInt((double)exchange_orders[i].volume));
             //--- set order prices
             if(res==MT_RET_OK)
                res=gateway_order->PriceOrder(exchange_orders[i].price_order);
             if(res==MT_RET_OK)
                res=gateway_order->PriceSL(exchange_orders[i].price_SL);
             if(res==MT_RET_OK)
                res=gateway_order->PriceTP(exchange_orders[i].price_TP);
             //--- set order type
             if(res==MT_RET_OK)
                res=gateway_order->Type(exchange_orders[i].type_order);
             //--- set order expiration type and time
             if(res==MT_RET_OK)
                res=gateway_order->TypeTime(exchange_orders[i].type_time);
             if(res==MT_RET_OK)
                res=gateway_order->TimeExpiration(exchange_orders[i].expiration_time);
             //--- set activation flags for exchange execution
             if(res==MT_RET_OK && m_api_exchange->SymbolGet(exchange_orders[i].symbol,exchange_symbol) && exchange_symbol.exec_mode==ExchangeSymbol::EXECUTION_EXCHANGE)
                res=gateway_order->ActivationFlags(IMTOrder::ACTIV_FLAGS_NO_EXPIRATION|IMTOrder::ACTIV_FLAGS_NO_LIMIT);
             //--- put login to comment
             str.Format(L"%I64u",exchange_orders[i].login);
             if(res==MT_RET_OK)
                res=gateway_order->Comment(str.Str());
             //--- set order setup time
             if(res==MT_RET_OK)
                res=gateway_order->TimeSetup(m_api_gateway->TimeCurrent());
             //--- add order to array
             if(res==MT_RET_OK)
                res=gateway_orders->Add(gateway_order);
             else
                gateway_order->Release();
            }
          else
             res=MT_RET_ERR_MEM;
         }
    //--- return result
       return(res);
      }

A MetaTrader 5 order is created for each external trading system's one by filling its ticket, external system ID, symbol, initial and current volume, prices, type, expiration time and type, adding time, activation flags and comment. Then, the order is added to the list.

Positions are converted using the CGateway::ConvertPositions method.
    
    
    MTAPIRES CGateway::ConvertPositions(const ExchangePositionsArray &exchange_positions,IMTPositionArray *gateway_positions) const
      {
       IMTPosition   *gateway_position=NULL;
       MTAPIRES       res             =MT_RET_OK;
    //--- check
       if(!m_api_gateway || !gateway_positions)
          return(false);
    //--- go through all positions
       for(UINT i=0;i<exchange_positions.Total() && res==MT_RET_OK;i++)
         {
          //--- skip empty positions
          if(exchange_positions[i].volume==0)
             continue;
          //--- get Gateway API position interface
          if((gateway_position=m_api_gateway->PositionCreate())!=NULL)
            {
             //--- set position symbol
             if(res==MT_RET_OK)
                res=gateway_position->Symbol(exchange_positions[i].symbol);
             //--- set position volume
             if(res==MT_RET_OK)
                gateway_position->Volume(SMTMath::VolumeToInt((double)abs(exchange_positions[i].volume)));
             //--- set position action
             if(res==MT_RET_OK)
               {
                if(exchange_positions[i].volume>0)
                   res=gateway_position->Action(IMTPosition::POSITION_BUY);
                else
                   res=gateway_position->Action(IMTPosition::POSITION_SELL);
               }
             //--- set position open price
             if(res==MT_RET_OK)
                res=gateway_position->PriceOpen(exchange_positions[i].price);
             //--- write login to the comment
             if(res==MT_RET_OK)
               {
                CMTStr32 comment;
                comment.Format(L"%I64u",exchange_positions[i].login);
                res=gateway_position->Comment(comment.Str());
               }
             //--- set digits amount
             if(res==MT_RET_OK)
                res=gateway_position->Digits(exchange_positions[i].digits);
             //--- add position to array
             if(res==MT_RET_OK)
                res=gateway_positions->Add(gateway_position);
             else
                gateway_position->Release();
            }
          else
             res=MT_RET_ERR_MEM;
         }
    //--- return result
       return(res);
      }

A MetaTrader 5 position is created for each external trading system's one by filling its symbol, volume, direction, Open price, accuracy and comment. Then, the position is added to the list.

Some data may be lost when synchronizing orders and positions in the MetaTrader 5 platform, for example orders or take profit and stop loss prices not passed to the external system if they are not stored in the external system or not filled by the gateway.  
---  
  
<a id="samplegateway-launch-and-setup"></a>
## SampleGateway Launch and Setup (#samplegateway-launch-and-setup)

To run the gateway sample, compile SampleGateway project and copy the obtained executable file (SampleGateway.exe or SampleGateway64.exe) to gateway\SampleGateway subdirectory of a history server working directory.

After SampleGateway application has been compiled and copied, it is time to configure the gateway. To do this, you should create the gateway configuration and set its parameters. Gateways configuration has been thoroughly described in ["Configuration of Gateways"](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_gateways/gateways_config) section. Gateway configuration includes adding a gateway and trading requests routing setup.

The gateway configuration is performed in the "Gateways" section of MetaTrader 5 Administrator.

![Gateway Setup](images/sample_gateway_common.png)

The following parameters on the "Common" tab must be set:

  * Module \- "SampleGateway" or "SampleGateway64" (according to the necessary bit count of the compiled SampleGateway), if the gateway is to be launched automatically (by a history server). In case a gateway is a remote one, "Remote Gateway" value should be used as a gateway module.
  * ID \- unique dealer identifier, on whose behalf the trading requests will be processed. Requests are routed to the gateway according to this identifier. The value "11" is shown in the provided example.
  * Trading server \- an external trading system server address in "ip:port" format. The default value in SampleGateway is "127.0.0.1:16838".
  * Trading login \- a user ID in an external trading system.
  * Trading password \- a user password in an external trading system.



User ID and password are used only for demonstration purposes in SampleGateway and SampleExchange. Therefore, "Trading login" and "Trading password" fields values may be left blank for this example. In an actual gateway these fields should be filled with the values provided by an external trading system provider.

The clients groups mask must be specified on the "Groups" tab. The gateway will receive trading requests from the clients included into the set groups list.

The mask of trading symbols available to the gateway must be specified on the "Symbols" tab. The gateway will translate quotes and perform trade operations for these symbols. Also, the settings will be automatically updated for them in case of symbols automatic importing Automatic symbols importing must be additionally allowed by enabling "Allow importing symbol settings" option.

![Configuring the symbols](images/sample_gateway_symbols.png)

Trading requests routing should be configured to allow trading requests from the client terminals to start getting to SampleGateway.

Open "Routing" section in the administrator terminal. A new routing rule should be added for SampleGateway. "Process to dealers" value should be set in "Perform action" field on the "Common" tab to allow clients' trading requests to be sent for processing to SampleGateway. Trading instruments mask must be specified in additional conditions ("Where conditions are").

In this example, all trading symbols have been moved to the new "SampleExchange" group from SampleExchange after the initial import. Therefore, "SampleExchange\*" value is specified for "Symbols" condition:

![Configuring routing](images/sample_gateway_routing_common.png)

SampleGateway should be added on "Dealers" tab:

![Configuring routing](images/sample_gateway_routing_dealers.png)

<a id="samplegateway-debugging"></a>
## SampleGateway Debugging (#samplegateway-debugging)

Correct command line corresponding to the gateway parameters should be generated to start debugging. Then the gateway application with the generated command line should be launched using a debugger. The application launch command line is generated based on the gateway settings.

SampleGateway should be created/used to start debugging in the "Gateways" section of the administrator terminal settings. "Remote Gateway" module should be used as the gateway module. Default gateway parameters downloading should be avoided:

![Remote Gateway](images/sample_gateway_remote.png)

When using "Remote Gateway" module, a history server does not launch the gateway process and initiates connection to the address specified in "Gateway server" field. The login and the password specified in "Gateway login" and "Gateway Password" fields are used during the process. Trading servers will also connect to Gateway API server port according to Gateway server, Gateway login and Gateway Password settings.

Parameters with the values equivalent to the settings of the gateway using "Remote Gateway" module should be used in the gateway launch command line:

  * /name: debugged gateway name. This name is used by Gateway API for different purposes. For example, the working directory of the gateway will be created using its name. It is "Sample Gateway" in our case.
  * /address: the gateway server port address, specified in "Gateway server" field at SampleGateway setup stage.
  * /login: login for connecting history and trade servers to SampleGateway, specified in "Gateway login" field.
  * /password: password for connecting history and trade servers to SampleGateway, specified in "Gateway password" field.



After all values have been specified, we will get the resulting parameters line of the gateway application launch:

"/name:Sample Gateway" "/address:127.0.0.1:16641" "/login:100" "/password:default"  
---  
  
Obtained application launch parameter line should be specified in Visual Studio in "Configuration Properties\Debugging" section of the project properties:

![Configuring debugging](images/sample_gateway_debug.png)

To start debugging, you should launch the gateway application using the already configured debugger and allow the gateway operation in MetaTrader 5 Administrator.

When debugging, it should be considered that history and trading servers will connect the gateway application according to the settings specified on "Timeouts" tab of the gateway settings. Reconnection [timeouts](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_gateways/gateways_config) values can be reduced to accelerate the platform servers connection to the gateway application.

<a id="sampleexchange-external-trading-system"></a>
## SampleExchange External Trading System (#sampleexchange-external-trading-system)

SampleExchange application emulating an external trading system operation has been developed to demonstrate SampleGateway trading mechanisms.

The basic functions of SampleExchange are:

  * accepting the client connection of SampleGateway (the application is a demo one and designed to accept only one connection);
  * submitting the settings of trading symbols to SampleGateway;
  * submitting the quote data to SampleGateway;
  * accepting trading requests from SampleGateway and their processing;
  * sending trade requests responses to SampleGateway.



Connection of SampleGateway SampleExchange external trading system has been implemented via sockets.

To launch SampleExchange, you should build SampleExchange project and launch the obtained SampleExchange.exe or SampleExchange64.exe file (depending on the built project bit count). The application is a console-based one accepting command line parameters at the input. The list of available parameters is shown during the application launch with "/?" command line parameter.

The address and the port, at which SampleExchange will wait for the gateway incoming connections, can be explicitly specified using /address:ip:port parameter. The default value is "127.0.0.1:16838".

After SampleExchange has been launched, it will wait for SampleGateway client connection. After the connection has been established, SampleExchange sends the settings of trading symbols to the gateway. After all the symbols have been sent, connection of the gateway and an external trading system is deemed to be synchronized From now on an external system starts sending quote data to the gateway and waits for trading requests from it.

All trading requests are transferred to SampleExchange external trading system by SampleGateway, regardless of their execution mode by a trading symbol.

SampleExchange accepts a trading request and generates a response to it. Bid and ask prices for a symbol, as well as a request processing result are specified in a response. Then it is sent to the gateway. The gateway converts the data from an external trading system format to MetaTrader 5 format and sends a response to a trading request to a client.

Exit SampleExchange application by pressing <Esc>.

Interaction of SampleGateway and SampleExchange external trading system can be observed in the gateway logs:

2012.06.05 08:27:15 GatewayAPI server started on 127.0.0.1:16641  
2012.06.05 08:27:25 127.0.0.1 '100': login (Trade Server build 630)  
2012.06.05 08:27:25 Trade '100': request all executions (received last execution ID with value=0)  
2012.06.05 08:27:25 GatewayAPI '100': try to connect as Main Server while History Server is not connected, waiting for History Server connection  
2012.06.05 08:27:25 127.0.0.1 '100': logout  
2012.06.05 08:27:26 127.0.0.1 '100': login (History Server build 630)  
2012.06.05 08:27:26 127.0.0.1 '100': login (Trade Server build 630)  
2012.06.05 08:27:26 Trade '100': request all executions (received last execution ID with value=0)  
2012.06.05 08:27:26 Gateway 'Sample Gateway' initialized  
2012.06.05 08:27:26 Gateway connecting to exchange server (127.0.0.1:16838)  
2012.06.05 08:27:26 Gateway connected to 127.0.0.1:16838  
2012.06.05 08:27:26 Gateway login successful  
2012.06.05 08:27:26 Gateway synchronized with exchange  
2012.06.05 08:28:48 Gateway '1001': request #13484772 received (prices for EURUSD.TEST 3.00)  
2012.06.05 08:28:48 Trade '100': request #13484772 performed on gateway in 125 ms  
2012.06.05 08:28:48 Gateway '1001': request #13484772 answered - Done  
2012.06.05 08:28:55 Gateway '1001': request #13484773 received (prices for EURUSD.TEST 3.00)  
2012.06.05 08:28:55 Trade '100': request #13484773 performed on gateway in 124 ms  
2012.06.05 08:28:55 Gateway '1001': request #13484773 answered - Done  
2012.06.05 08:28:59 Gateway '1001': request #13484774 received (#112 market buy 3.00 USDCHF.TEST)  
2012.06.05 08:28:59 Trade '100': request #13484774 performed on gateway in 110 ms  
2012.06.05 08:28:59 Gateway '1001': request #13484774 answered - Done  
2012.06.05 08:29:02 Gateway '1001': request #13484775 received (#113 exchange sell 3.00 USDJPY.TEST at market)  
2012.06.05 08:29:02 Trade '100': request #13484775 performed on gateway in 109 ms  
2012.06.05 08:29:02 Gateway '1001': request #13484775 answered - Done  
---

```

---

<a id='development-of-data-feeds-md'></a>
### 195. `Development-of-Data-Feeds.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Development of Data Feeds

[Previous](Symbol-and-Price-Translation.md) | [Next](NET-Implementation.md)

<a id="developing-data-feeds"></a>
# Developing Data Feeds (#developing-data-feeds)

Creating the new MetaTrader 5 platform, we've done our best to facilitate integration with gateways and data feeds. For this purpose, we've developed MetaTrader 5 Gateway API - a special library for developers.

In this library, we've hidden all technical details of interaction with the trading platform and have provided an opportunity to manage integration using simple methods. Now, developer's code does not depend on the internal changes and is always operable.

The library is developed for working at win32 and x64 platforms and is included into the MetaTrader 5 distributive. Using MetaTrader 5 Gateway API, developers can implement their own trade gateways, as well as data feeds.

This section describes an example of writing a simple data feed for the MetaTrader 5 platform in C++.

<a id="how-do-data-feeds-work-in-metatrader-5"></a>
## How do Data Feeds work in MetaTrader 5? (#how-do-data-feeds-work-in-metatrader-5)

The main objective of a Data Feed is to receive quotes and news from external providers and transform these data into MetaTrader 5 format.

![How do Data Feeds work in MetaTrader 5?](images/datafeed_scheme.png)

Exchanging news and quotes data with MetaTrader 5 trading platform is done entirely via MetaTrader 5 History Server. Data Feed is a medium between History Server and external data source.

Each Data Feed is implemented as a standalone application, so the failure in its work does not affect the work of the platform. All Data Feeds processes are reentrant. You can run one Data Feed application several times, and each time new data source is provided.

Communicating with History Server is implemented via encrypted network connection. Using a network connection to communicate with History Server allows the trading platform to use Data Feeds that work on remote network computers. Data Feed application provides server port for connection, while the History Server creates client connection to the server port of Data Feed.

If the Data Feed executable file is stored in the 'datafeed' sub-folder of History Server, then application Start and Stop is done by History Server. When working remotely, Data Feed is a service that accepts and handles incoming connections from History Servers. To each Data Feed you can connect several servers.

<a id="metatrader-5-gateway-api-description"></a>
## MetaTrader 5 Gateway API Description (#metatrader-5-gateway-api-description)

The main task for a developer is to transfer all the data, obtained in the MetaTrader 5 Gateway API. For application programmers we can compose the following algorithm to work with this API:

  * Initialization. At this stage, developer has to load the library.
  * Obtaining and running server port interface. All interaction with API is done via server port interface. This interface contains methods of data management and sending. When you create a user interface API, developer must specify his own notification handler. Using this handler API will notify the developer about new connections of History Servers and their parameters (quotes symbols, operation mode, additional parameters). This information only notifies a user and its use is optional.
  * Sending data. Server port interface contains all the necessary methods for sending data to connected History Servers.
  * Exiting. At this stage, a developer has to release server port interface and unload the library.



MetaTrader 5 Gateway API is described in a single 'MT5APIGateway.h' file and implemented in the 'MT5APIGateway.dll' and 'MT5APIGateway64.dll' files for win32 and x64 platforms, respectively. For an application that uses API, it is necessary that these files must be available. Simply copy them into the application folder.

The library exports a few simple functions:

  * [MTGatewayVersion](Exported-Functions/MTGatewayVersion.md) \- returns the version of the Gateway API.
  * [MTGatewayCreateLocal](Exported-Functions/MTGatewayCreateLocal.md) \- creates and returns an instance of the gateway interface taking into account its description and parameters passed in the command line. In the command line from History Server passed are the time zone and the server port number, on which interface must be started as a server accepting incoming connections. Command line is also used to obtain Data Feed description. By passing command line parameters to the library, we've freed developers from parsing line parameters, time zone initialization and Data Feed description formatting. This method is used only by Data Feeds, controlled by History Server.
  * [MTGatewayCreate](Exported-Functions/MTGatewayCreate.md) \- creates and returns an instance of gateway interface.



When creating a gateway interface, we need to pass to it a correctly filled out [MTGatewayInfo](../Structures/MTGatewayInfo.md) structure. This structure contains the description of a data feed and its default settings.

<a id=""></a>
##  (#)

<a id="metatrader-5-gateway-api-description"></a>
## MetaTrader 5 Gateway API Description (#metatrader-5-gateway-api-description)

The major task of a developer is to transmit quoting data for the MetaTrader 5 Gateway API. From the point of view of an application programmer, the following algorithm for working with this API can be used:

  * Initialization. At this stage, the developer loads the library.
  * Get and run the gateway interface. All interaction with the API is done through the gateway's abstract interface. To enable the creation of data feeds, this interface provides methods for managing and sending quoting data. When creating an interface, an API developer should specify their own event handler. Through this handler, the API will notify the developer about new server connections and their parameters (for data feeds, these are quoted symbols, operation mode, and additional parameters). This information is optional and thus you may choose not to use it.
  * Send data. The gateway interface provides all the necessary methods for sending quoting data to all connected History servers.
  * Complete operations. At this stage, the developer releases the gateway interface and unloads the library.



MetaTrader 5 Gateway API is described in one file, 'MT5APIGateway.h', and it is implemented in files 'MT5APIGateway.dll' and 'MT5APIGateway64.dll', for win32 and x64 platforms respectively. Please make sure that these files are available, otherwise the application using the API will not work. To make the files available, simply copy them to the application directory.

The library exports a few simple functions:

  * [MTGatewayVersion](Exported-Functions/MTGatewayVersion.md) \- returns the Gateway API version.
  * [MTGatewayCreateLocal](Exported-Functions/MTGatewayCreateLocal.md) \- creates and returns an instance of the gateway interface, taking into account its description, with the parameters passed on the command line. The following parameters are passed on the command line from the History Server: time zone values and the port number on which the gateway interface will start running as a server that accepts incoming connections. The command line is also used to get the data feed description. By passing the command-line arguments to the library, we eliminate the need for the developer to parse the string parameters, to initialize the time zone and to generate the data feed description. This method is only used by the data feeds managed by the History server.
  * [MTGatewayCreate](Exported-Functions/MTGatewayCreate.md) \- creates and returns an instance of the gateway interface.



When creating a gateway interface, it must be passed a correctly filled [MTGatewayInfo](../Structures/MTGatewayInfo.md) structure. This structure contains the data feed description and its default settings.

<a id="representation"></a>
## Data feed presentation to users: logo and description (#representation)

MetaTrader 5 supports the loading of the data feed logo and description from resources. Use this option to present your product in the [data feed showcase in MetaTrader 5 Administrator](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_feeds), as well as to provide documentation on the spot.

![Data feed presentation in MetaTrader 5 Administrator](images/datafeed_showcase.png)

Add resources with the "DESCRIPTION" type and with the following IDs to your project:

  * 1000 — module description in free form, in UTF-8 format. Use an HTML document without classes and style, only with simple tags: h3, p, ul, ol, b, i. Standard Administrator terminal styles will be applied to the description and it will naturally fit into the interface.
  * 1001 — square logo for the showcase.
  * 1002 — square logo for high-resolution monitors.
  * 1003 — rectangle logo for the list of data feeds and the details page.
  * 1004 — rectangle logo for high-resolution monitors.



An example of a .RC project file block:
    
    
    1000 DESCRIPTION "res\\description.html"
    1001 DESCRIPTION "res\\200x200.png"
    1002 DESCRIPTION "res\\400x400.png"
    1003 DESCRIPTION "res\\360x100.png"
    1004 DESCRIPTION "res\\720x200.png"

When loading the data feed module, the history server will pass this data to the main server, from which the information will be displayed in MetaTrader 5 Administrator.

<a id="imtgatewayapi-interface"></a>
## IMTGatewayAPI Interface (#imtgatewayapi-interface)

The main interaction with API is done via [IMTGatewayAPI](Main-Interface.md) interface. Access to this interface is gained using functions exported by the library. To make it more simple, in 'MT5APIGateway.h' file there is implemented interface factory, which automatically loads correct 32 or 64 bit library and provides access to the exported functions. Example of creating server interface via factory:
    
    
    //+------------------------------------------------------------------+
    //| Example of gateway interface creation                            |
    //| using the interface factory                                      |
    //+------------------------------------------------------------------+
    int wmain(int argc,wchar_t** argv)
      {
       CMTGatewayAPIFactory  apifactory;
       IMTGatewayAPI        *gateway=NULL;
       MTGatewayInfo         info;
    //--- library initialization
       if(apifactory.Initialize()!=MT_RET_OK)
          return(-1);
    //--- generation of gateway description
       Info(info);
    //--- server interface creation
       if(apifactory.Create(info,&gateway,argc,argv)!=MT_RET_OK)
          return(-1);
     
    //---
    //--- use the gateway interface to send quoting data to a History Server
    //---
     
    //--- free the server interface
       server->Release();
    //--- shutting down the interface factory
       apifactory.Shutdown();
    //--- Successful
       return(0);
      }

The entire [IMTGatewayAPI](Main-Interface.md) interface is absolutely thread-safe - you can call methods of this interface any time from any thread of executed commands. All IMTGatewayAPI interface methods can be divided into methods of management and methods of sending price data to History Servers.

Let's consider methods of gateway management:

  * [Start](Main-Interface/Server/Start.md) \- start receiving incoming connections to the gateway by IP address and port specified in the 'address' parameter. The gateway will notify users by calling virtual methods of IMTGatewaySink interface. Developers can override notification methods with their own by implementing class, inherited from IMTGatewaySink. More detailed description of IMTGatewaySink interface is below.
  * [Stop](Main-Interface/Server/Stop.md) \- stop receiving incoming connections by the gateway.
  * [Release](Main-Interface/Common-Functions/Release.md) \- releasing gateway interface. After calling this method gateway object is destroyed, and the pointer to gateway interface becomes unavailable. Do not release interface by calling 'delete', because with this call API will not know about interface deletion. Interface should always be released using Release() method.
  * [ClientAdd](Main-Interface/Client-Connection/ClientAdd.md) \- using this method developer specifies allowed authentication data (login and password) for incoming connections. You can add multiple logins and passwords.
  * [ClientAllowIP](Main-Interface/Client-Connection/ClientAllowIP.md) \- adding IP addresses, from which incoming connection is allowed. If no addresses are added, then incoming connections are allowed from all addresses. You can add multiple addresses. You can add multiple addresses.
  * [ServerIP](Main-Interface/Server/IP.md) \- getting IP address, on which incoming connections are listened and received.
  * [ServerPort](Main-Interface/Server/Port.md) \- as a return value, the method passes the port number that is running and listening to incoming connections.
  * [ServerConnections](Main-Interface/Server/Connections.md) \- as a return value, the method passes the number of authorized and working incoming connections at the time of call.



Example of gateway management:
    
    
    //--- ...
    //--- add data to authorize gateway incoming connections
       if(gateway->ClientAdd(123,L"Password")!=MT_RET_OK)
         {
          //--- release the interface and exit
          gateway->Release();
          return(-1);
         }
    //--- add IP from which incoming connection to the gateway is allowed
       if(gateway->ClientAllowIP(L"192.168.0.2")!=MT_RET_OK)
         {
          //--- release the interface and exit
          gateway->Release();
          return(-1);
         }
    //--- start receiving incoming connections, address of the gateway - 192.168.0.1, port - 16384
       if(gateway->Start(&client,L"192.168.0.1:16384")!=MT_RET_OK)
         {
          //--- release the interface and exit
          gateway->Release();
          return(-1);
         }
    //--- wait till ESC pressing
       while(_getwch()!=27)
         {
     
          //---
          //--- here we can receive and send quotes and news
          //---
     
          //--- delay
          Sleep(100);
         }
    //--- gateway stopping
       gateway->Stop();
    //--- //--- 
       gateway->Release();
    //--- ....

Let's consider methods of sending data to History Servers.

There are 4 methods of transferring data in server port interface. All these methods work asynchronously. This means that the managing will return to the developer's code immediately after placing data to the API buffer for sending. Let's consider these methods in details:

  * [SendTickStats](Main-Interface/Quote-and-News-Feeds/SendTickStats.md) \- sending ticks statistics. This method accepts array of [MTTickStat](../Structures/MTTickStat.md) structures, counting 'stats_total' elements.
  * [SendTicks](Main-Interface/Quote-and-News-Feeds/SendTicks.md) \- sending ticks. This method accepts array of [MTTick](../Structures/MTTick.md) structures, counting 'ticks_total' elements. 
  * [SendBookDiffs](Main-Interface/Quote-and-News-Feeds/SendBookDiffs.md) \- sending changes in depth of market. This method accepts array of [MTBookDiff](../Structures/MTBookMTBookDiff.md) structures, counting 'bookdiffs_total' elements. MTBookDiff structure has a special feature, that contains an array of [MTBookItem](../Structures/MTBookItem.md) structures, and the number of structures is indicated in the 'items_total' value. These elements describe the change in depth of market.
  * [SendNews](Main-Interface/Quote-and-News-Feeds/SendNews.md) \- sending news. This method accepts array of [MTNews](../Structures/MTNews.md) structures, counting 'news_total' elements.
  * [LoggerOut](Main-Interface/Common-Functions/LoggerOut.md) \- adding entry into the API journal. For your convenience, API has its own journal. All technical details of working with journal - journal filename correct formation, journal file size controlling, receiving latest journal entries by request from History Server, etc. - are hidden from developers Example of using journal methods:


    
    
    gateway->LoggerOut(MTLogErr,L"last error(%d)",GetLastError());

<a id="filling-mtbookdiff-structure"></a>
### Filling MTBookDiff Structure (#filling-mtbookdiff-structure)

Each element of the aggregated depth of market is unique in type and price. The [MTBookDiff](../Structures/MTBookMTBookDiff.md) structure contains information about volume changes for a given type and price in the form of an array of MTBookItem [MTBookItem](../Structures/MTBookItem.md) elements. One MTBookDiff structure contains changes only for one instrument, described in the 'symbol' value of the structure.

Here are depth of market elements' change types and History Server actions, when receiving this types of elements to form an aggregated depth of market:

  * ItemReset - on receiving element with this type History Server will clean the aggregated depth of market for a given symbol.
  * ItemSell, ItemBuy - on receiving MTBookItem structure with this type, History Server will look for aggregated depth of market's element by type and price, given in MTBookItem. If the element is not found, then a new element (of MTBookItem type and price) is added to the aggregated depth of market. If the element is found in the aggregated depth of market, then element volume changes by the volume value, specified in the MTBookItem structure. If zero volume is indicated in the MTBookItem structure, then element, found in the aggregated depth of market, is deleted.



The volume of element change in the aggregated depth of market, described in MTBookItem, can be both positive and negative.

<a id="filling-mtnews-structure"></a>
### Filling MTNews Structure (#filling-mtnews-structure)

The 'language' field must contain news language identifier from the Windows Languages Identifier table. This field specifies the language of news, and is used when sending news to Client Terminals, in which only certain languages are selected.

News category is used for news filtration. String, separated by the '\' symbol, can be passed as a value of this parameter. Separator is used to define subcategories and allows you to build a tree of available news categories. This allows you to filter news in Client Terminal. Category example: "DJ Newswires\PrimeTass\Real-Time news".

[MTNews](../Structures/MTNews.md) structure is special, as it contains a pointer to dynamically allocated buffer for the news body. The length of news body is indicated in the 'body_len' field (in characters). Thus, to send the news body, a developer needs to create a memory buffer of desired size and copy the news body into it. Pointer to the buffer and buffer size in characters must be copied into the 'body' and 'body_len' field, respectively. After calling the method of sending news, you need to remove previously created buffer for news body in order to prevent memory leaks.

To send high priority news you should set the FLAG_PRIORITY flag in the 'flags' field.

<a id="imtgatewaysink-interface"></a>
## IMTGatewaySink Interface (#imtgatewaysink-interface)

[IMTGatewaySink](Event-Interface.md) interface is described in the 'MT5APIGateway.h' file and is used to organize API feedback from the developer's program In case of certain event, API calls the appropriate method of the IMTGatewaySink interface. All methods of this interface are virtual. This means that developers can create a class, inherited from IMTGatewaySink, and implement its own logic in these method, if needed.

In practice, class, inherited from IMTGatewaySink, is needed only when implementing Data Feed, managed by History Server. If Data Feed is implemented in the form of independent remote service, developers don't need feedback from API This means that there's no need to create a class, inherited from IMTGatewaySink. You can immediately use the IMTGatewaySink implementation from the 'MT5APIGateway.h' file.

All IMTGatewaySink methods calls are produced sequentially in time, in one of threads of commands handling pool. So the code in the overridden IMTClient methods must be thread-safe.

Let's consider IMTGatewaySink methods in details:

  * [HookServerConnect](Event-Interface/HookServerConnect.md) \- this call is made from API as a result of receiving of incoming connection. The address from which the connection is performed, type of the MetaTrader server that is connecting (History Server or Trade Server) and the server login is passed to the interface. This method can be used to restrict external connections by address and login.
  * [OnServerDisconnect](Event-Interface/OnServerDisconnect.md) \- notice about closing the connection. The method parameters coincide with the parameters passed in HookServerConnect.
  * [OnGatewayShutdown](Event-Interface/OnGatewayShutdown.md) \- notice about shutting down the server with the given login. If there are no external connections, API calls this method every 2 minutes with login 0. This is done in order to stop Data Feed, if there are no connections to History Server for a long time. Similarly to OnConfig(), you can skip overriding this method, if Data Feed works as an independent remote service. If Data Feed is controlled by History Server, then application must be shut down on this call.
  * [OnGatewayConfig](Event-Interface/OnGatewayConfig.md) \- this call is made after the HookServerConnect call and reports about the ser parameters of the data feed on the History Server that is connecting. Using the [IMTConFeeder](../Configuration-Interfaces/Data-Feeds/IMTConFeeder.md) interface you can get additional settings for external connection. These parameters are set in MetaTrader 5 Administrator when adding or editing Data Feed.



Description of the main methods of the [IMTConFeeder](../Configuration-Interfaces/Data-Feeds/IMTConFeeder.md) interface used to create a data feed:
    
    
    //--- data for external connection
       virtual LPCWSTR   Server(void) const=0;                // server address for external connection
       virtual LPCWSTR   Login(void) const=0;                 // login for external connection
       virtual LPCWSTR   Password(void) const=0;              // password for external connection
       //--- additional parameters
       virtual UINT      Mode(void) const=0;                  // operation mode(IMTConFeeder::EnFeedersMode)
       virtual LPCWSTR   Categories(void) const=0;            // news categories
     //--- navigation through symbols for which we receive quotes
       virtual UINT      SymbolTotal(void) const=0;           // total number of symbols whose quotes are received
       virtual LPCWSTR   SymbolNext(const UINT pos) const=0;  // getting symbol name by its number

External connection is used to get quotes and news from provider. Depending on how you connect to the external source, it's necessary to specify connection parameters, such as address, login, password. These parameters can be obtained by calling the methods of the IMTConFeeder interface.

As a result of calling the [Categories](../Configuration-Interfaces/Data-Feeds/IMTConFeeder/Categories.md) method we receive the root news category, set in MetaTrader 5 Administrator when adding or editing Data Feed. Ability to enter news category, when adding Data Feed, can filter out all news of this Data Feed. Upon receiving news their final category will be formed by adding news category itself to the root category. The root category can be empty. In this case Category() will return a string with a zero length.

For example, in Data Feed settings the root category has "MT5Datafeed" value, and the news passed to API has "DJ Newswires\PrimeTass\Real-Time news" category. After receiving this news API will assign to it the final "MT5Datafeed\DJ Newswires\PrimeTass\Real-Time news" category. In this example, the result of Category() call will be the "MT5Datafeed" string.

As noted above, how to use obtained settings - is up to developer. If Data Feed is fully managed by History Server, you need to start external connection using specified settings. If Data Feed works as an independent service, you can skip overriding the call and can set external connections parameters in advanced settings of service, for example, in a special configuration file.

<a id="example-of-data-feed-implementation"></a>
## Example of Data Feed implementation (#example-of-data-feed-implementation)

Examples, given in this article, are complete and will allow developers to quickly implement their own data sources. Let's consider Data Feed, which is fully controlled by History Server. Example is implemented in C++ in Visual Studio 2005/2008. You can download free Express edition from [Microsoft website](https://www.microsoft.com/express/Downloads/).

To create your own project, you can copy the ready implementation from the article. We offer typical ready-to-use solution, on which you can quickly and easily create your own Data Feed. Developers only have to correctly form Data Feed description and implement work with external connections: connection and data processing.

Let's consider organization of typical solution and methods, that should be implemented, in more details.

Data Feed's work is mostly implemented in the CMTDatafeedApp class. It is the main application class, and is inherited from the [IMTGatewaySink](Event-Interface.md) interface. Thus, overriding the virtual methods of the IMTGatewaySink interface, we're getting notifications from API. CMTDatafeedApp encapsulates two main entities: interface of server port API and external connection class.

To correctly form source description the in the Info(MTGatewayInfo& info) method of CMTDatafeedApp class, developers need to form the correct data describing Data Feed.

CDataSource external connection class implements access to external connections. For example, using object of this class, you can connect to data source, obtain quotes and news. CDataSource hides the details of external connection implementation. This kind of API add-on of quotes data, given by provider.

CDataSource works in a separate thread of commands execution. This is done for long pauses in interaction with external connections not to freeze Data Feed application.

Thus, the CMTDatafeedApp class has two interfaces: API and interface of external connection to data source. All CMTDatafeedApp work is reduced to correct initialization of these two interfaces and their management.

Also, to ease logging we've implemented the CLogger class in our project. After initializing object of this class by server port interface it can be conveniently used to add records to API journal. In order for logging to be available anywhere in the program, we've created global ExtLogger object of the CLogger class.

Let's consider described processes in details on the basis of source codes. Almost immediately after start an object of the CMTClient main managing class is created in application:
    
    
    //+------------------------------------------------------------------+
    //| Entry Point                                                      |
    //+------------------------------------------------------------------+
    int wmain(int argc,wchar_t** argv)
      {
       CMTDatafeedApp datafeed;
    //--- display banner
       Banner();
    //--- initialize application
       if(!datafeed.Initialize(argc,argv))
          return(-1);
    //--- main method of application
       datafeed.Run();
    //--- shutting down
       datafeed.Shutdown();
    //--- exit
       return(0);
      }

As you can be seen from the code, the main application function does initializes, starts and shuts down the main class of application. In the initialization method CMTDatafeedApp creates the server port interface of API and the object of external connections:
    
    
    //+------------------------------------------------------------------+
    //| Initialization |
    //+------------------------------------------------------------------+
    bool CMTDatafeedApp::Initialize(int argc,wchar_t** argv)
      {
       MTGatewayInfo info;
       MTAPIRES      ret=MT_RET_OK;
    //--- checking
       if(!argv)
          return(false);
    //--- library initialization
       if(m_apifactory.Initialize()!=MT_RET_OK)
          return(false);
    //--- filling MTGatewayInfo structure
       Info(info);
    //--- creating gateway interface
       ret=m_apifactory.Create(info,&m_gateway,argc,argv);
    //--- if this is the History server receiving information, exist
       if(ret==MT_RET_OK_NONE)
          return(false);
    //--- checking
       if(ret!=MT_RET_OK || m_gateway==NULL)
          return(false);
    //--- initialize logger
       ExtLogger.SetGateway(m_gateway);
    //--- creating data feed object
       if((m_source=new CDataSource())==NULL)
          return(false);
    //--- Successful
       return(true);
      }

In the Run method of CMTDatafeedApp class the thread of external connection is started and API server port is run. After start API server port is ready to receive incoming connections. In case of a successful launch, the application runs in the external connections control loop, until work is complete:
    
    
    //+------------------------------------------------------------------+
    //| Running application                                              |
    //+------------------------------------------------------------------+
    bool CMTDatafeedApp::Run()
      {
       bool started=false;
    //--- checking
       if(!m_gateway || !m_source)
          return(false);
    //--- starting to process external connection
       if(started=m_source->Start(m_gateway))
         {
          //--- starting to receive incoming connections
          started=m_gateway->Start(this)==MT_RET_OK;
         }
    //--- if running, setting the flag of operation of the controlling thread
       if(started)
          InterlockedExchange(&m_workflag,1);
    //--- main loop of controlling the connection
       while(InterlockedExchangeAdd(&m_workflag,0))
         {
          //--- checking external connection
          if(!m_source->Check())
             break;
          //--- delay
          Sleep(SLEEP_TIMEOUT);
         }
    //--- gateway stopping
       m_gateway->Stop();
    //--- completing data feed operation
       m_source->Shutdown();
    //--- Successful
       return(true);
      }

Thus, applications work is distributed across multiple threads. Application is multi-thread This somewhat complicates the architecture, but also allows to significantly enhance performance and reliability. To introduce application's dynamic model let's describe used threads and problems, solved by them, in details:

  * Main application thread \- used to control external connections and is responsible for application initialization and it's correct shutdown.
  * External connection thread \- works in the CDataSource class and is used to control and process data of external connection.
  * Network commands thread pool \- pool is hidden in API and is used to exchange data and to process control commands of connected History Servers. Callbacks of methods, overridden in IMTGatewaySink, from API are also done by one of the threads of this pool. API guarantees the impossibility of calling one method of IMTGatewaySink interface from more than one thread at a time. This means that more that one callback from API from more than one thread is not possible.



Data Feed developers must add code of controlling external connections to the appropriate CDataSource methods. Therefore, let's consider this class in details.

Object of CDataSource class accepts a pointer to the [IMTGatewayAPI](Main-Interface.md) interface. This makes the transmitting of received data to connected History Servers possible.

As noted above, work with external connection is implemented in a separate thread. The main loop of the thread is implemented in the ProcessThread method:
    
    
    //+------------------------------------------------------------------+
    //| External connection thread                                       |
    //+------------------------------------------------------------------+
    void CDataSource::ProcessThread(void)
      {
    //--- loop of controlling external connection
       while(InterlockedExchangeAdd(&m_workflag,0)>0)
         {
          //--- analyzing connection state; if it starts connection, then connection is processed
          if(GetState()==STATE_CONNECTSTART)
             ProcessConnect();
          //--- external connection successfully established, processing the data
          if(GetState()==STATE_CONNECTED)
             ProcessData();
          //--- delay
          Sleep(100);
         }
    //--- shutdown
       Shutdown();
      }

Managing CDataSource class is carried out from the main CMTDatafeedApp application class. The following public methods are used for management:

  * bool Start(IMTGatewayAPI *gateway) \- starting the thread of external connection processing.
  * bool Shutdown() \- shutting down external connection. Calling this method will close external connection and stop the thread of processing.
  * bool Init(const IMTConFeeder *config) \- initialization. After calling this method, the thread of CDataSource class will try to establish connection with parameters specified in the IMTConFeeder interface. Using that interface one can obtain all necessary information, such as: external connection address, login, password, etc.
  * bool Check() \- checking external connection for a hang-up, if the connection is not hanged up, then this method will returns true, otherwise - false.
  * LONG GetState() \- obtaining the state of external connection.
  * LONG SetState(LONG state) \- force setting the new state of connection.



Data Feed developers need to implement their own specific methods of external connection. All details of working with external connections are concentrated in the two methods of CDataSource class:

  * bool ProcessConnect \- in this method you must connect to external data source and return connection result.
  * bool ProcessData() \- in this method implementation you must obtain data from external source and pass them to the server port by means of the IMTGatewayAPI interface. You must return the correct result of these actions.



To get started, you need to copy the "MT5APIGateway.dll" and "MT5APIGateway64.dll" libraries from API application folder to folder with Data Feed executable. 

```

---

<a id='event-interface-md'></a>
### 195. `Event-Interface.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Event Interface

[Previous](Main-Interface/User-Settings/SettingsGet.md) | [Next](Event-Interface/OnServerDisconnect.md)

# IMTGatewaySink Interface

IMTGatewaySink interface is used to notify on the events happening at a trading platform. It also allows to manage a platform connection to Gateway API.

IMTGatewaySink interface contains the following methods:

Method | Purpose  
---|---  
[OnServerDisconnect](Event-Interface/OnServerDisconnect.md) | A handler of the event of the end of connection to one of the MetaTrader 5 platform components (server).  
[OnServerSynchronized](Event-Interface/OnServerSynchronized.md) | A handler of the event of data synchronization between Gateway API and one of the MetaTrader 5 platform (server) components.  
[OnServerSymbolAdd](Event-Interface/OnServerSymbolAdd.md) | A handler of the event of symbol adding.  
[OnServerSymbolDelete](Event-Interface/OnServerSymbolDelete.md) | A handler of the event of symbol removal.  
[OnGatewayConfig](Event-Interface/OnGatewayConfig.md) | A handler of the event of passing a gateway/data feed own configuration from a history server connected to it.  
[OnGatewayStart](Event-Interface/OnGatewayStart.md) | A handler of the following event: Gateway API is synchronized with the platform and is ready for work.  
[OnGatewayStop](Event-Interface/OnGatewayStop.md) | OnGatewayStart inverse events hadler. Notifies on the fact that Gateway API is not synchronized with the platform and not ready for work.  
[OnGatewayShutdown](Event-Interface/OnGatewayShutdown.md) | A handler of the event notifying about the trading platform shutdown or gateway/data feed disconnection.  
[OnGatewayAccountAnswer](Event-Interface/OnGatewayAccountAnswer.md) | A handler of the event of requesting information about a client from MetaTrader 5 platform.  
[OnGatewayAccountSet](Event-Interface/OnGatewayAccountSet.md) | A handler of the event of modifying information about a client via [IMTGatewayAPI::GatewayAccountSet](Main-Interface/Synchronizing-Trading-Data/GatewayAccountSet.md) method.  
[OnDealerLock](Event-Interface/OnDealerLock.md) | A handler of the event of capturing (blocking) of a successive trade request from a requests queue.  
[OnDealerAnswer](Event-Interface/OnDealerAnswer.md) | A handler of the event notifying on a request confirmation or execution result.  
[HookServerConnect](Event-Interface/HookServerConnect.md) | The hook for managing MetaTrader 5 platform components connections to Gateway API.  
[HookGatewayPositionsRequest](Event-Interface/HookGatewayPositionsRequest.md) | The hook for receiving states of trading accounts used by the gateway to operate in an external system.  
[HookGatewayPositionsCheck](Event-Interface/HookGatewayPositionsCheck.md) | Hook for positions verification. This method is reserved for future use.  
[HookGatewayOrdersRequest](Event-Interface/HookGatewayOrdersRequest.md) | The hook for receiving the state of the client's current pending orders in an external trading system.  
[HookGatewayAccountRequest](Event-Interface/HookGatewayAccountRequest.md) | The hook for synchronizing client's trading data with an external trading system.

```

---

<a id='exported-functions-md'></a>
### 195. `Exported-Functions.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Exported Functions

[Previous](NET-Implementation.md) | [Next](Exported-Functions/MTGatewayVersion.md)

# Exported Functions

MT5APIGatewayAPI.dll library (and its 64-bit version), which is used for the interaction between the application and MetaTrader 5 trading platform, exports several functions:

Function | Description  
---|---  
[MTGatewayVersion](Exported-Functions/MTGatewayVersion.md) | Returns Gateway API library version.  
[MTGatewayCreate](Exported-Functions/MTGatewayCreate.md) | Creates a new [IMTGatewayAPI](Main-Interface.md) interface object and returns a pointer to it.  
[MTGatewayCreateLocal](Exported-Functions/MTGatewayCreateLocal.md) | Creates a new [IMTGatewayAPI](Main-Interface.md) interface object with predetermined parameters and returns a pointer to it.

```

---

<a id='interaction-of-the-platform-and-md'></a>
### 195. `Interaction-of-the-Platform-and.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Interaction of the Platform and

[Previous](README.md) | [Next](Trade-Operations-in.md)

# Interaction of the Platform and Gateway API

The MetaTrader 5 trading platform exchanges data with the Gateway API using the client-server technology, where the platform acts as a client and the Gateway API acts as a server. To protect the Gateway API server from unauthorized connection authorization is used. Parameters of the server port of the Gateway API are specified in the Gateway Server field, and authentication parameters are set in the Gateway Login and Gateway Password fields of the gateway or data feed (via the MetaTrader 5 Administrator or the appropriate interfaces — [IMTConFeeder](../Configuration-Interfaces/Data-Feeds/IMTConFeeder.md) and [IMTConGateway](../Configuration-Interfaces/Gateways/IMTConGateway.md)).

The process of starting the gateway/data feed begins after completing presets and including its configuration in the MetaTrader 5 Administrator. Below is the sequence of actions performed during the start:

  * The [IMTGatewayAPI::Start](Main-Interface/Server/Start.md) method is called to start the server port of the Gateway API. After that, the Gateway API begins to accept incoming connections from the platform components. The process of data synchronization between the platform and the Gateway API begins.
  * First a history server is connected to the Gateway API. It passes the configuration of the gateway/data feed. At this stage, the work of the Gateway API is defined: whether it will operate as a gateway or as a data feed. Until the history server is connected, other components cannot be connected.
  * If an application is a data feed, other components of the platform are not connected. Transmission of quotes and/or news begins.
  * If the application is a gateway, then the main trading server additionally connects to the Gateway API. It passes the trading platform settings of symbols, groups, etc.
  * Further, all other trading servers of the platform are connected.
  * After synchronization the [IMTGatewaySink::OnGatewayStart](Event-Interface/OnGatewayStart.md) event is called.



```

---

<a id='main-interface-md'></a>
### 195. `Main-Interface.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Main Interface

[Previous](CMTGatewayAPIFactory/Version.md) | [Next](Main-Interface/Enumerations.md)

# Main Interface IMTGatewayAPI

Main interaction with API is carried out through the IMTGatewayAPI interface. [Exported functions](Exported-Functions.md) and [factory](CMTGatewayAPIFactory.md) must be used to get the access to the interface. All IMTGatewayAPI interface is fully thread safe. Its methods can be called at any time from any commands execution thread.

Description of the IMTGatewayAPI interface methods is divided into the following sections:

  * [Enumerations](Main-Interface/Enumerations.md)
  * [Common Functions](Main-Interface/Common-Functions.md)
  * [Server](Main-Interface/Server.md)
  * [External Connection Status](Main-Interface/External-Connection-State.md)
  * [Client Connection](Main-Interface/Client-Connection.md)
  * [Quote and News Streams](Main-Interface/Quote-and-News-Feeds.md)
  * [History Data](Main-Interface/History-Data.md)
  * [Tick Data](Main-Interface/Tick-Data.md)
  * [Users](Main-Interface/Users.md)
  * [Configuration databases](Main-Interface/Configuration-Databases.md)
  * [Trade Databases](Main-Interface/Trade-Databases.md)
  * [Trade Requests](Main-Interface/Trade-Requests.md)
  * [Gateway Symbols](Main-Interface/Gateway-Symbols.md)
  * [Processing Trade Requests](Main-Interface/Processing-Trade-Requests.md)
  * [Controlling Positions in External System](Main-Interface/Controlling-Positions-in-External-System.md)
  * [Controlling Orders in External System](Main-Interface/Controlling-Orders-in-External-System.md)
  * [Synchronizing Trading Data](Main-Interface/Synchronizing-Trading-Data.md)
  * [Mail Database](Main-Interface/Mail-Database.md)
  * [Custom Settings](Main-Interface/User-Settings.md)



```

---

<a id='net-implementation-md'></a>
### 195. `NET-Implementation.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / .NET Implementation

[Previous](Development-of-Data-Feeds.md) | [Next](Exported-Functions.md)

# Implementation of MetaTrader 5 Gateway API in .NET

The MetaTrader 5 Gateway API includes a ready implementation in .NET. The implementation is available in the form of ready to use DLLs. To be able to use their functions, you need to add them to a project.

The libraries are available in [SDK installation folder]\Libs:

  * MetaQuotes.MT5CommonAPI(64).dll — library of common API interfaces ([configuration bases](../Configuration-Interfaces/README.md) and [databases](../Database-Interfaces/README.md)).
  * MetaQuotes.MT5GatewayAPI(64).dll — Gateway API library.



Aside from DLLs, the package includes examples TextFeeder.NET and UniFeeder.NET. They are available in [Gateway API installation folder]\Examples.

  * .NET Framework 4.7.2 or newer and all [Visual C++ Redistributable for Visual Studio packages starting from 2015](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads) are required to develop applications.


  * .NET implementation is a wrapper over the main Gateway API C++ library. Therefore, the MT5APIGateway(64).dll file is also required.

  
---  
  
## Basic Terms

A short glossary of the terms used:

  * Managed — code, method, class running in the .NET CLI environment with the so called garbage collection management via the [GC class](https://msdn.microsoft.com/ru-ru/library/system.gc%28v=vs.110%29.aspx). The class controls the system garbage collector — the service that automatically releases unused memory.
  * Native — the native code, method, class running directly in the operating system environment.
  * Native code or API — classes and interfaces of API.
  * Managed wrapper — a .NET class providing an interface of the native API without inheritance.
  * Unsafe code — code in C# or any other managed language that can access pointers, low-level memory management, etc.



## Use the reference of the native Gateway API for the .NET wrapper — almost all functions and methods are identical

All managed wrappers are identical to their native interfaces except for the methods that use arrays. For example:
    
    
    // Native API
    MTAPIRES  ChartUpdate(LPCWSTR symbol,const MTChartBar *bars,const UINT bars_total)=0;
    // Managed API C#
    MTAPIRES  ChartUpdate(string symbol,MetaQuotes.MT5CommonAPI.MTChartBar[] bars)...
    // Managed API C++
    MTAPIRES  ChartUpdate(String^ symbol,array<MetaQuotes.MT5CommonAPI.MTChartBar>^ bars)...

## No Exceptions

Managed wrappers do not generate exceptions. If any library calls generate exceptions, the wrapped code will not let them out.

## Always Use Factory

All managed wrappers of API interfaces should only be created using factories, special methods (for example, [UserCreate](Main-Interface/Users/UserCreate.md), [UserCreateAccount](Main-Interface/Users/UserCreateAccount.md), etc.). This will prevent from passing incorrect pointers to the native code and from using unsafe client code. A separate factory is implemented for each API library.

## Register Event Handler Classes, Do Not Allow Exceptions

For sink classes, you must call the RegisterSink method in the child class constructor and check the return value. This is connected with the possibility to process errors binding a native sink interface to its managed wrapper.

It is important to not let exceptions out of the sink classes handler methods. Otherwise, logging exceptions will be impossible. It is especially important not to let the exceptions out of the hook methods, which may cause unpredictable behavior of the trading platform.

## Use the "using" Operator

All API managed wrappers inherit the [IDisposable](https://msdn.microsoft.com/ru-ru/library/system.idisposable%28v=vs.110%29.aspx) interface, which provides a mechanism for releasing unmanaged resources. Use the ["using"](https://msdn.microsoft.com/ru-ru/library/yh598w02.aspx) operator for easy and correct use of IDispose objects.
    
    
    void UserFunction()
      {
    ...
       using(CIMTConSymbol symbol=m_gateway.SymbolCreate())
         {
          symbol.Symbol("<SymbolName>");
    ...
          symbol.Path("<SymnolPath>");
    ...
          m_gateway.SymbolAddPreliminary(symbol);
         }
         //--- Will surely destroy the 'symbol' object and its native resources
      }

In the above example, the 'user' object and its native resources will be released once code execution exits the 'using' block. Without using the "using" operator, it is unknown when and under what circumstances the object will be deleted.

> To explicitly release resources, you can also use the 'Release' and 'Dispose' methods of managed wrappers. These methods are similar.

## ToArray Methods in Managed Wrappers for Working with Arrays

ToARray methods are implemented in all managed wrappers for working with array objects, such as [CIMTUserArray](../Database-Interfaces/Users/IMTUserArray.md), [CIMTOrderArray](../Database-Interfaces/Trade/Orders/IMTOrderArray.md) and others. These methods create an array and fill it with the elements of the array source object.

  * No element copying is performed during ToArray call. Elements in the new array refer to the elements of the original array. Therefore, when an element is destroyed by calling Dispose or Release in one array, the appropriate element becomes invalid (destroyed) on the other array. Do not call Dispose/Release methods for the []ToArray array elements.
  * Use the Detach method to detach an element from the array object (CIMT*Array).
  * If the source array does not have elements, ToArray returns an empty array, not nullptr.



## Memory Management

Memory in .NET implementation is managed by the programmer. The programmer must explicitly call the Dispose or Release methods for the created objects in the required places of the application. In .NET finalizers memory is not released automatically: if a .NET wrapper object is not released through Dispose, it will lead to memory and native API object leaks.

When working with the .NET implementation, a situation may occur where two or more wrappers refer to the same native object. For example, this may occur when using the aforementioned ToArray methods. In this case, the programmer must control the lifetime of the objects and avoid access to already released objects.

> Dispose and Release perform the same function, i.e. they release the previously created object. Dispose is designed to match the .NET style and enable the use of the 'using' construct.

## Operation Speed

The speed of calling wrapped methods is much slower than calling its native analogue. This is connected with the check of the native pointer, managed arguments, etc.

Speed ​​of calls of some wrapped methods that return arrays, particularly arrays of structures, can slow down performance significantly. Example — creating a copy of the array:
    
    
    array<INT64>^ CIMTGatewayAPI::UserLogins(MTRetCode% res)
            {
             res=MTRetCode::MT_RET_ERR_MEM;
             array<INT64>^ result=nullptr;
             if(m_this)
               {
                INT64* narray=NULL;
                UINT   total =0;
                //--- Call implementation
                if((res=(MTRetCode)m_this->UserLogins(res))==MTRetCode::MT_RET_OK)
                  {
                   res=(MTRetCode)NativeToManagedArrayCopy(result,narray,total);
                   //--- release the native array
                   if(narray) m_this->Free(narray);
                  }
               }
             return(result);
            }

Example of using the .NET wrapper of Gateway API
    
    
    namespace SomeClientNamespace
      {
       using MetaQuotes.MT5CommonAPI;
       using MetaQuotes.MT5GatewayAPI;
       using System;
    ...
       class CSomeClientClass
         {
          //--- Gateway API
          public CIMTGatewayAPI m_gateway=null;
              public CDataSource    m_source=null;
    ...
          public MTRetCode Initialize()
            {
             MTRetCode res=MTRetCode.MT_RET_ERROR;
             //--- Initialize the factory
             if((res=SMTGatewayAPIFactory.Initialize())!=MTRetCode.MT_RET_OK)
               {
                LogOutFormat("SMTGatewayAPIFactory.Initialize failed - {0}",res);
                return(res);
               }
             //--- Receive the API version
             uint version=0;
             if((res=SMTGatewayAPIFactory.GetVersion(out version))!=MTRetCode.MT_RET_OK)
               {
                LogOut("SMTGatewayAPIFactory.GetVersion failed - {0}",res);
                return(res);
               }
             //--- Compare the obtained version with the library one
             if(version!=SMTGatewayAPIFactory.GatewayAPIVersion)
               {
                LogOutFormat("Gateway API version mismatch - {0}!={1}",version,SMTGatewayAPIFactory.GatewayAPIVersion);
                return(MTRetCode.MT_RET_ERROR);
               }
             //--- Create an instance
             m_gateway=SMTGatewayAPIFactory.CreateGateway(SMTGatewayAPIFactory.GatewayAPIVersion,out res);
             if(res!=MTRetCode.MT_RET_OK)
               {
                LogOut("SMTGatewayAPIFactory.CreateGateway failed - {0}",res);
                return(res);
               }
             //--- For some reasons, the creation method returned OK and the null pointer
             if(m_gateway==null)
               {
                LogOut("SMTGatewayAPIFactory.CreateGateway was ok, but GatewayAPI is null");
                return(MTRetCode.MT_RET_ERR_MEM);
               }
             //--- All is well
             LogOutFormat("Using GatewayAPI v. {0}", version);
                     //--- create the data feed
             m_source=new CDataSource();            
             return (res);
            }
    ...
          //+------------------------------------------------------------------+
          //| Data feed operation                                              |
          //+------------------------------------------------------------------+
          public bool Run(string address=null)
            {
             bool started=false;
             //--- Check
             if(m_gateway==null || m_source==null)
                return(false);
             //--- start processing external connections
             if(started=m_source.Start(m_gateway))
               {
                //--- start receiving incoming connections
                started=m_gateway.Start(this,address)==MTRetCode.MT_RET_OK;
               }
             //--- set the flag if the launch is successful
             if(started)
                Interlocked.Exchange(ref m_workflag,1);
             //--- main cycle of external connections management
             while(Interlocked.Add(ref m_workflag,0)!=0)
               {
                //--- check the external connection
                if(!m_source.Check())
                   break;
                //--- waiting
                Thread.Sleep((int)constants.SLEEP_TIMEOUT);
               }
             //--- end operation
             m_gateway.Stop();
             m_source.Shutdown();
             //--- All is well
             return(true);
            }
    ...
          //+------------------------------------------------------------------+
          //| Receive the data feed description                                |
          //+------------------------------------------------------------------+
          public override void OnGatewayConfig(UInt64 login,CIMTConFeeder config)
            {
             //--- performing operation
             if(m_source!=null)
                m_source.Init(config);
            }
    ...
         }
      }

```

---

<a id='readme-md'></a>
### 195. `README.md`

```markdown
[🏠 Document Start](../README.md) / Gateway API

[Previous](../Manager-API/Interface-of-Manager-API-Events/Interface-of-Events-OnTradeAccountSet.md) | [Next](Interaction-of-the-Platform-and.md)

# MetaTrader 5 Gateway API

MetaTrader 5 Gateway API is a set of tools for integrating the MetaTrader 5 platform with other trading systems. Using Gateway API, you can implement custom gateways and data sources.

Gateway API is a set of functions, a description of the data structure used, identifiers and virtual interface of gateways; supplied in the form of C++ interfaces, 32 and 64 bit DLL-libraries and source codes examples.

All technical details concerning interaction with the trading platform are hidden in DLL library, which gives the possibility to control integration using simple methods. Thus, developer's code does not depend on the internal changes and is always operable.

  * [Interaction of the Platform and Gateway API](Interaction-of-the-Platform-and.md)
  * [Trade Operations in Gateway API](Trade-Operations-in.md)
  * [Developing and Debugging Gateways](Development-and-Debugging-of-Gateways.md)
  * [Symbol and Price Translation](Symbol-and-Price-Translation.md)
  * [Developing Data Feeds](Development-of-Data-Feeds.md)
  * [.NET Implementation](NET-Implementation.md)
  * [Exported Functions](Exported-Functions.md)
  * [CMTGatewayAPIFactory](CMTGatewayAPIFactory.md)
  * [Main Interface](Main-Interface.md)
  * [Event Interface](Event-Interface.md)



```

---

<a id='symbol-and-price-translation-md'></a>
### 195. `Symbol-and-Price-Translation.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Symbol and Price Translation

[Previous](Development-and-Debugging-of-Gateways.md) | [Next](Development-of-Data-Feeds.md)

# Symbol and Price Translation

Gateways are able to import necessary sets of trading symbols, manage their settings, update them if necessary and provide quotes. Gateway settings allow you to easily change data passed from the external system:

  * Rename trading symbols
  * Convert quotes
  * Copy price data to different symbols



The settings are available on the Translations tab of each gateway in the administrator terminal. In API, they are represented by the [IMTConGatewayTranslate](../Configuration-Interfaces/Gateways/IMTConGatewayTranslate.md) interface.

> To let a gateway manage the settings of trading tools on MetaTrader 5 side, enable the "Allow importing symbols settings" option ([IMTConGateway::GATEWAY_FLAG_IMPORT_SYMBOLS (#engatewayflags)](../Configuration-Interfaces/Gateways/IMTConGateway/Enumerations.md#engatewayflags)).

## Renaming trading symbols

Data on any symbol can be passed from an external system to the MetaTrader 5 platform under any name. For example, if the symbol name in an external system is EURUSD_ABC, and it is called EURUSD in the MetaTrader 5, enter EURUSD in the "Symbol" field and EURUSD_ABC in the "Source" field.

![Renaming the symbol passed by the gateway](images/translations_rename.png)

> If another source of quotes is already specified in symbol settings ([IMTConSymbol::Source](../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md)), this symbol cannot be specified as the receiver symbol. Also symbols with the disabled delivery of real-time quotes from data feeds ([IMTConSymbol::TICK_REALTIME (#entickflags)](../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags)) cannot be specified as receivers. Conversion settings containing such symbols will be ignored by the platform.

Use the * mask for renaming multiple symbols. For example, in order to add the .delayed suffix to all gateway symbols, specify:

![Renaming multiple symbols passed by the gateway](images/translations_rename_mass.png)

> Only simple masks with a single * symbol are supported. Settings with more complicated masks (for example, having two * or ! negation symbol) are ignored.

In order to duplicate data to different symbols on the MetaTrader 5 side, create several entries in the Translations section. In the example below, the entire available set of gateway symbols is passed to the platform in two instances: with the .1 and .2 suffixes.

![Duplicating symbols from an external system in the MetaTrader 5 platform](images/translation_split.png)

> A gateway behavior changes depending on the translations configuration phase:

## Price translation

A gateway broadcasts a flow of quotes from an external trading system to the MetaTrader 5 platform and is able to change it on the fly. Clients receive prices according to the translation settings. However, while processing trading operations on the gateway and passing them back to the external system, initial (not transformed) prices are used.

If trading tool names in the platform are not different from the ones in the external system, simply specify a symbol name in the platform and translation value for Bid and Ask prices.

![Translating the quotes](images/translation_price.png)

The above screenshot shows price conversion: at every tick, the Bid price will be reduced by 3 points, and the Ask price will be increased by 2 points. Below is a schematic example of the conversion:

External system | >>> | ask price | EURGBP 0.83004 | >>> | MetaTrader 5 server  
---|---|---|---|---|---  
MetaTrader 5 server | >>> | ask price | EURGBP 0.83006 | >>> | Client terminal  
Client terminal | >>> | buy limit | EURGBP 0.83006 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit | EURGBP 0.83004 | >>> | External system  
External system | >>> | buy limit execution | EURGBP 0.83004 | >>> | MetaTrader 5 server  
MetaTrader 5 server | >>> | buy limit execution | EURGBP 0.83006 | >>> | Client terminal  
  
A broker gains 2 pips of profit in this example. The price is sent to the client terminal only after the correction, so the clients work only with the corrected prices. If no correction is set for a symbol, the client will work with the original prices submitted by an external system.

Using the previously described possibilities of symbols mass renaming and duplication, you are able to customize different flows of quotes. For example, original and converted ones:

![Creating two quote flows: original and converted](images/translation_price_split.png)

The .wide suffix stands for converted quotes, while the .original stands for non-converted ones.

## Features of trade operations

If only one translation parameter or no parameters at all are set for a gateway, trades are conducted without any peculiarities since the platform is able to match symbols on its side with the ones at the external trading system.

If more than one translation parameter is set for the gateway, the platform attempts to match the symbols correctly. For example, the two translation parameters are set for the gateway:

![The EURUSD symbol has two translation settings in the external system: EURUSD.1 and EURUSD.2](images/translations_trade_map.png)

If an order is placed on the platform side, a symbol in the external system response is defined by the original order ticket. For example, a trader places an order #145269 Buy 1.00 EURUSD.2. It is sent to the external system as #145269 Buy 1.00 EURUSD. When receiving a response, the platform converts the symbol back to EURUSD.2 by the original order ticket.

However, there are some trading operations/events that are not preceded by placing an order on the trading platform side. For example, charging a variation margin in an external system. In that case, the platform cannot clearly define which of the two symbols the event is related to: EURUSD.1 or EURUSD.2.

In this situation, the platform attempts to select the correct symbol by its availability to certain accounts the event is related to. For example, if only EURUSD.2 is available for an account, the platform performs an operation for it. Availability of symbols for clients is defined on the Symbols tab of the group settings ([IMTConGroup::Symbol*](../Configuration-Interfaces/Groups/IMTConGroup/SymbolAdd.md)).

If both symbols are available for the account, the operation is performed for the first one in the translation list. It is EURUSD.1 in our example.

Thus, if there are multiple translation settings, the following rule is used: trading operations are performed for the first symbol available for a client group. All subsequent translation settings are used only to pass price data.

The table below contains trading operations and events ([trade execution types (#entradeexecutions)](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Enumerations.md#entradeexecutions)) preceded by placing an order on MetaTrader 5 side, which means that symbols can be accurately matched for them regardless of the number of translation settings. For other operations, the platform attempts to define the necessary symbol by its availability for a client group.

A symbol is accurately matched by an original order | A symbol is defined by its availability for a client  
---|---  
TE_ORDER_NEW_REQUEST TE_ORDER_NEW TE_ORDER_FILL TE_ORDER_REJECT TE_ORDER_MODIFY_REQUEST TE_ORDER_MODIFY TE_ORDER_MODIFY_REJECT TE_ORDER_CANCEL_REQUEST TE_ORDER_CANCEL TE_ORDER_CANCEL_REJECT TE_ORDER_CHANGE_ID TE_ORDER_CLOSE_BY | TE_DEAL_EXTERNAL TE_DEAL_REPO TE_EOS_CANCEL_DAILY_ORDERS TE_EOS_VARIATION_MARGIN TE_EOS_VARIATION_MARGIN TE_EOS_SETTLEMENT TE_EOS_TRANSFER TE_EOS_CANCEL_ALL_ORDERS TE_EOS_ROLLOVER

```

---

<a id='trade-operations-in-md'></a>
### 195. `Trade-Operations-in.md`

```markdown
[🏠 Document Start](../README.md) / [Gateway API](README.md) / Trade Operations in

[Previous](Interaction-of-the-Platform-and.md) | [Next](Development-and-Debugging-of-Gateways.md)

<a id="trade-operations-in-gateway-api"></a>
# Trade Operations in Gateway API (#trade-operations-in-gateway-api)

In the trade interaction of the Gateway API and the MetaTrader 5 trading platform, two main entities can be singled out — a trade request and a trade execution.

A trade request ([IMTRequest](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequest.md)) is formed on the side of the MetaTrader 5 platform as a result of a trade order sent by a client. A trade request notifies the Gateway API of trade operations on the platform side.

A trade execution ([IMTExecution](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTExecution.md)) is formed on the side of the Gateway API. It is used to notify the MetaTrader 5 platform of events in an external trading system. Based on the trade execution, the appropriate action is performed in MetaTrader 5.

<a id="queue-of-trade-requests"></a>
## Queue of Trade Requests (#queue-of-trade-requests)

In accordance with the ideology of the MetaTrader 5 trading platform, customer request management is carried out through a queue of trade requests. A gateway written with the help of the Gateway API acts as a dealer, who works with the queue, receiving the queue status, capturing and processing trade requests, and then reporting the results of their processing.

> Trade queues of all trade servers of one platform are gathered into one common queue, with which the gateway works.

To connect to the queue of trade requests, the Gateway API uses the method [IMTGatewayAPI::DealerStart](Main-Interface/Processing-Trade-Requests/DealerStart.md). After the execution of the method, the queue of trade requests is downloaded in the application, and [events associated with trade requests](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequestSink.md) (IMTRequestSink::OnRequestAdd, IMTRequestSink::OnRequestUpdate and IMTRequestSink::OnRequestDelete) start arriving.

After connecting to the queue, the gateway can start [to handle trade requests](Trade-Operations-in.md).

In general, the procedure of processing trade requests from an application in Gateway API is as follows:

<a id="receiving-a-trade-request-from-the-queue"></a>
## Receiving a Trade Request from the Queue (#receiving-a-trade-request-from-the-queue)

The first step is to receive a trade request from the queue and to determine its type:

  * To connect to the queue of trade requests, the method [IMTGatewayAPI::DealerStart](Main-Interface/Processing-Trade-Requests/DealerStart.md) is used on the server. When connecting, you should also specify the flag of automatic capturing of new trade requests from the queue [IMTGatewayAPI::DEALER_FLAG_AUTOLOCK (#endealerrequestflags)](Main-Interface/Enumerations.md#endealerrequestflags).
  * After that trade requests will be locked in the queue for executing trade operations and will be forwarded to the handler [IMTGatewaySink::OnDealerLock](Event-Interface/OnDealerLock.md).
  * Upon receiving a request in the handler, you should analyze the type of action performed by the request, using the [IMTRequest::Action](../Database-Interfaces/Trade/Trade-Requests/IMTRequest/Requests-Action.md) method, as well as the request type using the [IMTRequest::Type](../Database-Interfaces/Trade/Trade-Requests/IMTRequest/Requests-Type.md) method.



When connecting to the queue of requests, it is not recommended to use the flags for receiving additional information ([DEALER_FLAG_USER, DEALER_FLAG_ACCOUNT (#endealerrequestflags)](Main-Interface/Enumerations.md#endealerrequestflags) etc.) without the need. This reduces the overall performance of the application.  
---  
  
<a id="mt5-side"></a>
## Processing Trade Operations on the Side of MetaTrader 5 (#mt5-side)

If a request does not require any action on the side of an external trading system (for example, if a Buy Stop Limit order is placed, which should be handled on the side of MetaTrader 5), the request should be confirmed. To do this, use the [IMTGatewayAPI::DealerConfirmCreate](Main-Interface/Processing-Trade-Requests/DealerConfirmCreate.md) method to form the confirmation object [IMTConfirm](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTConfirm.md) with the response code [MT_RET_REQUEST_DONE](../Return-Codes/Trade-Requests.md) ([IMTConfirm::Retcode](../Database-Interfaces/Trade/Trade-Requests/IMTConfirm/Requests-Retcode.md)) and pass it in the [IMTGatewayAPI::DealerAnswerAsync](Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md) method. After that the processing of a trade request is completed.

<a id="processing-trade-operations-in-an-external-system"></a>
## Processing Trade Operations in an External System (#processing-trade-operations-in-an-external-system)

If a request requires some actions on the side of an external trading system, it should be confirmed with the response code [MT_RET_REQUEST_PLACED](../Return-Codes/Trade-Requests.md). Confirmation with this response code is used to notify the platform that this request will be processed in an external system.

Use the [IMTGatewayAPI::DealerConfirmCreate](Main-Interface/Processing-Trade-Requests/DealerConfirmCreate.md) method to form the confirmation object [IMTConfirm](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTConfirm.md) with the response code [MT_RET_REQUEST_PLACED](../Return-Codes/Trade-Requests.md) ([IMTConfirm::Retcode](../Database-Interfaces/Trade/Trade-Requests/IMTConfirm/Requests-Retcode.md)) and pass it in the [IMTGatewayAPI::DealerAnswerAsync](Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md) method.
    
    
    //+------------------------------------------------------------------+
    //| Confirm request for the client                                   |
    //+------------------------------------------------------------------+
    MTAPIRES SendRequestConfirm(const IMTRequest *request)
      {
       MTAPIRES    res=MT_RET_OK;
       IMTConfirm* confirm;
    //--- checks
       if(!m_api_gateway || !request)
          {
           ExtLogger.Out(MTLogErr,L"failed to confirm trade request");
           return(MT_RET_ERR_PARAMS);
          }
    //--- create and sent a confirmation object
       if(confirm=m_api_gateway->DealerConfirmCreate())
          {
           confirm->ID(request->ID();
           confirm->Retcode(MT_RET_REQUEST_PLACED);
           if(m_api_gateway->DealerAnswerAsync(confirm)!=MT_RET_OK)
              {
               ExtLogger.Out(MTLogErr,L"failed to confirm trade request");
               res=MT_RET_ERROR;
              }
         }
       confirm->Release();
    //--- return result
       return(res);
      }

Next, depending on the type of the request being processed, you should notify the trading platform of what operation will be performed on the side of the external trading system. Use the [IMTGatewayAPI::DealerExecutionCreate](Main-Interface/Processing-Trade-Requests/DealerExecutionCreate.md) method to create an object of trade execution [IMTExecution](../Database-Interfaces/Trade/Trade-Requests/Requests-IMTExecution.md) and specify the appropriate type of operation [IMTExecution::Action](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Action.md) in it (the type of operation is passed as a value of the [IMTExecution::EnTradeExecutions (#entradeexecutions)](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Enumerations.md#entradeexecutions)) enumeration. For example, at an attempt to place a new order in the external system, you must create an object of trade execution of type IMTExecution::TE_ORDER_NEW_REQUEST. The execution object should be passed in the [IMTGatewayAPI::DealerExecuteAsync](Main-Interface/Processing-Trade-Requests/DealerExecuteAsync.md) method.

> Unlike IMTConfirm based [request execution on the platform side (#mt5-side)](Trade-Operations-in.md#mt5-side), processing of requests via trade executions (IMTExecution) is fully asynchronous. It means that a change in the order state in the platform fully depends on the gateway by which the order was placed. It is guaranteed that after returning control from the IMTGatewayAPI::DealerExecuteAsync method, the execution will be delivered to the MetaTrader 5 trading server, even if the trading server and/or gateway is restarted.
    
    
    //+------------------------------------------------------------------+
    //| Notify the platform about sending a request to external system   |
    //+------------------------------------------------------------------+
    MTAPIRES SendExecutionConfirm(const IMTRequest *request)
      {
       MTAPIRES      res=MT_RET_OK;
       IMTExecution* execution;
    //--- checks
       if(!m_api_gateway || !request)
          {
           ExtLogger.Out(MTLogErr,L"failed to create execution");
           return(MT_RET_ERR_PARAMS);
          }
    //--- create trade execution
       if(execution=m_api_gateway->DealerExecutionCreate())
          {
    //--- specify the order ticket (using initial request) and the execution type only
           execution->Order(request->ResultOrder());
           execution->Action(IMTExecution::TE_ORDER_NEW_REQUEST);
           if(m_api_gateway->DealerExecuteAsync(execution)!=MT_RET_OK)
              {
               ExtLogger.Out(MTLogErr,L"failed to send execution");
               res=MT_RET_ERROR;
              }
         } 
       execution->Release();
    //--- return result
       return(res);
      }

Then you can send a command to the external trading system to execute the corresponding operation (for example, through the FIX protocol).

If the external trading system reports that the operation succeeded, you will need to create another confirmation object of the appropriate type. For example, if a new order has been successfully placed in an external trading system, you should use the method [IMTGatewayAPI::DealerExecutionCreate](Main-Interface/Processing-Trade-Requests/DealerExecutionCreate.md) to create an object of trade execution and specify the type of operation [IMTExecution::TE_ORDER_NEW (#entradeexecutions)](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Enumerations.md#entradeexecutions) in it. Next, you need to pass this object in the [IMTGatewayAPI::DealerExecuteAsync](Main-Interface/Processing-Trade-Requests/DealerExecuteAsync.md) method. After this, the appropriate order will be created in the MetaTrader 5 platform.
    
    
    //+------------------------------------------------------------------+
    //| Notify about placing an order in external system                 |
    //+------------------------------------------------------------------+
    MTAPIRES SendExecutionNewOrder(const ExchangeOrder &exchange_order)
      {
       MTAPIRES      res=MT_RET_OK;
       IMTExecution* execution;
    //--- check
       if(!m_api_gateway)
          {
           ExtLogger.Out(MTLogErr,L"failed to create new order execution");
           return(MT_RET_ERR_PARAMS);
          }
    //--- create trade execution
       if(execution=m_api_gateway->DealerExecutionCreate())
          {
    //--- fill fields according to the trade execution type
          execution->Order(exchange_order.mt_ticket);
          execution->OrderExternalID(exchange_order.ext_ticket);
          execution->Login(exchange_order.mt_login);
          execution->OrderVolume(exchange_order.volume);
          execution->Symbol(exchange_order.symbol);
          execution->Action(IMTExecution::TE_ORDER_NEW);
           if(m_api_gateway->DealerExecuteAsync(execution)!=MT_RET_OK)
              {
               ExtLogger.Out(MTLogErr,L"failed to send new order execution");
               res=MT_RET_ERROR;
              }
         } 
       execution->Release();
    //--- return result
       return(res);
      }

In case of order execution (full or partial) on the side of the external trading system, you should form a confirmation object of type [IMTExecution::TE_ORDER_FILL (#entradeexecutions)](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Enumerations.md#entradeexecutions), with its [IMTExecution::Deal*](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-DealVolume.md) parameters filled.
    
    
    //+------------------------------------------------------------------+
    //| Notify about filling an order in external system                 |
    //+------------------------------------------------------------------+
    MTAPIRES SendExecutionOrderFill(const ExchangeOrder &exchange_order)
      {
       MTAPIRES      res=MT_RET_OK;
       IMTExecution* execution;
    //--- check
       if(!m_api_gateway)
          {
           ExtLogger.Out(MTLogErr,L"failed to create new order execution");
           return(MT_RET_ERR_PARAMS);
          }
    //--- create trade execution
       if(execution=m_api_gateway->DealerExecutionCreate())
          {
    //--- fill fields according to the trade execution type
           execution->Order(exchange_order.mt_ticket);
           execution->Symbol(exchange_order.symbol);
           execution->DealAction(exchange_order.type);
           execution->DealVolume(exchange_order.volume);
           execution->DealVolumeRemaind(0);              // 0 means the whole volume of the order is filled
           execution->DealPrice(exchange_order.price);   // price at which the order is filled
           execution->Action(IMTExecution::TE_ORDER_FILL);
           if(m_api_gateway->DealerExecuteAsync(execution)!=MT_RET_OK)
              {
               ExtLogger.Out(MTLogErr,L"failed to send new order execution");
               res=MT_RET_ERROR;
              }
          } 
       execution->Release();
    //--- return result
       return(res);
      }

In case of trade order modification on the side of the external trading system, you should form a confirmation object of type [IMTExecution::TE_ORDER_MODIFY (#entradeexecutions)](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Enumerations.md#entradeexecutions), with its [IMTExecution::Order*](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-OrderPrice.md) parameters filled (depending on what parameters of the order have been modified).

If the external trading system reports that the operation failed, form a trade execution with one of [IMTExecution::TE_*_REJECT (#entradeexecutions)](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Enumerations.md#entradeexecutions) types. For example, if a new order has not been placed, use type IMTExecution::TE_ORDER_REJECT, for a failed order modification, use IMTExecution::TE_ORDER_MODIFY_REJECT, etc.

After that the processing of a trade operation is completed.

> In each case, the parameters that correspond to the type of operation executed in the external trading system, should be filled in the trade execution object. Example:

<a id="executions"></a>
## A Database of Trade Executions (#executions)

The gateway and the trade server store information about trade executions in order to maintain correct operation in case of failures or connection interruptions:

  * The executions.dat file on the server side. The number of the last trade execution processed by the server (A) is stored in this file. When the next execution is received, the number of the last processed execution is overwritten in this file.
  * Files executions-*.dat and executions-*.idx are stored on the gateway side. They store the number of the last execution sent to a trade server (B), as well as a database of executions, which are ready for sending.



When connection is established, the server sends to the gateway the number of the last processed execution (A). The gateway analyzes this information and sends to the server all executions from its executions-*.dat database, whose numbers are greater than the one sent by the server. Thus, trading executions will not be missed even in case of a failure, since after the restoration of connection the gateway will pass to the server all unsent executions, which are stored in its database on a disk. 

If the number (A) received by the gateway from the server is greater than the last sent execution (B), which is also greater than the numbers of all executions in the gateway database, then it is considered that the execution databases have been changed on the gateway side or on the server side. An appropriate message is written to the gateway log in this case:

2018.04.16 15:12:55.111 TradeExecutions last execution id 13226 on the Trade Server 1 is greater than last execution id 13208 in the gateway database   
2018.04.16 15:12:55.112 TradeExecutions probably, 'executions-1.dat' on the gateway side or 'executions.dat' on the server side was changed, numbering will be continued from 13209  
---  
  
No executions will be skipped in this case. The server will process all executions sent by the gateway. The numbering of executions in the server database will continue from the last execution number sent by the gateway (B+1).

> Do not delete or change the databases of executions manually. Also, do not move these databases between different servers. This can lead to serious errors in the operation of the trading platform and the gateway.

```

---

<a id='cmtgatewayapifactory-create-md'></a>
### 195. `CMTGatewayAPIFactory/Create.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [CMTGatewayAPIFactory](../CMTGatewayAPIFactory.md) / Create

[Previous](Shutdown.md) | [Next](LicenseCheck.md)

# CMTGatewayAPIFactory::Create

Create an instance of the [IMTGatewayAPI](../Main-Interface.md) interface.

C++
    
    
    MTAPIRES  CMTGatewayAPIFactory::Create(
       MTGatewayInfo&  info,          // The MTGatewayInfo structure
       IMTGatewayAPI** gateway,       // A pointer to the pointer to the API interface
       int             argc=0,        // The number of command line parameters
       wchar_t**       argv=NULL      // Command line parameters
       )

.NET
    
    
    CIMTGatewayAPI  SMTGatewayAPIFactory.CreateGateway(
       MTGatewayInfo   info,          // The MTGatewayInfo structure
       string[]        arguments,     // Command line parameters
       out MTRetCode   res            // Response code
       )

### Parameters

**info**  
[in] TheMTGatewayInfostructure that describes the parameters of the gateway/data feed module.

**gateway**  
[out] A pointer to a pointer to the created instance of theIMTGatewayAPIinterface.

**argc=0**  
[in] The number of additional parameters of a command line that is used for running the gateway/data feed. The default value is 0.

**argv=NULL**  
[in] Additional parameters of the command line that is used for running the gateway/data feed. The default value is NULL.

### Return Value

An indication of a successful execution is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

Gateways/data feeds support the launch with the [additional command line parameters (#param)](../Exported-Functions/MTGatewayCreateLocal.md#param). In particular, the /description command line parameter is additionally used by the history server to get the description of the gateway/data feed module. Always pass the command line parameters to the CMTGatewayAPIFactory::Create method, so that the module is correctly downloaded and managed by the history server.

  * in command line parameters passed to CMTGatewayAPIFactory::Create (/name:XXX /address:XXX), or
  * in the [configuration file (#config)](https://support.metaquotes.net/ru/docs/mt5/platform/administration/admin_gateways/gateway_service#config) (name=XXX, address=XXX)



```

---

<a id='cmtgatewayapifactory-initialize-md'></a>
### 195. `CMTGatewayAPIFactory/Initialize.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [CMTGatewayAPIFactory](../CMTGatewayAPIFactory.md) / Initialize

[Previous](../CMTGatewayAPIFactory.md) | [Next](Shutdown.md)

# CMTGatewayAPIFactory::Initialize

Loading of Gateway API library and all [functions exported by it](../Exported-Functions.md).

C++
    
    
    MTAPIRES  CMTGatewayAPIFactory::Initialize()

.NET
    
    
    MTRetCode  SMTGatewayAPIFactory.Initialize()

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

The method determines the application bitness (32 or 64-bit) and loads an appropriate library.

  * In the directory where the application executable is located.
  * In the parent directory, then in the next upper-level directory and so on, up to five levels up from the executable files directory.
  * Using the path from the system PATH variable.



```

---

<a id='cmtgatewayapifactory-licensecheck-md'></a>
### 195. `CMTGatewayAPIFactory/LicenseCheck.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [CMTGatewayAPIFactory](../CMTGatewayAPIFactory.md) / LicenseCheck

[Previous](Create.md) | [Next](Version.md)

# CMTGatewayAPIFactory::LicenseCheck

Gateway/data feed module usage license verification.

C++
    
    
    static MTAPIRES  CMTGatewayAPIFactory::LicenseCheck(
       IMTGatewayAPI*  gateway,      // Pointer to the IMTGatewayAPI interface
       LPCWSTR         name          // The name of the module
       )

.NET
    
    
    static MTRetCode  SMTGatewayAPIFactory.LicenseCheck(
       CIMTGatewayAPI  gateway,      // Pointer to the IMTGatewayAPI interface
       string          name          // The name of the module
       )

### Parameters

**gateway**  
[in] Pointer to theIMTGatewayAPIinterface for gateway/data feed module license verification.

**name**  
[in] The name of the gateway/data feed that is to be verified for license. Module's unique name must be preliminarily determined in the program code.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

This factory method is provided to ease the license verification process. Comprehensive description of the verification algorithm can be found at the [IMTGatewayAPI::LicenseCheck](../Main-Interface/Common-Functions/LicenseCheck.md) function section.

```

---

<a id='cmtgatewayapifactory-shutdown-md'></a>
### 195. `CMTGatewayAPIFactory/Shutdown.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [CMTGatewayAPIFactory](../CMTGatewayAPIFactory.md) / Shutdown

[Previous](Initialize.md) | [Next](Create.md)

# CMTGatewayAPIFactory::Shutdown

Gateway API library unloading.

C++
    
    
    MTAPIRES  CMTGatewayAPIFactory::Shutdown()

.NET
    
    
    MTRetCode  SMTGatewayAPIFactory.Shutdown()

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='cmtgatewayapifactory-version-md'></a>
### 195. `CMTGatewayAPIFactory/Version.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [CMTGatewayAPIFactory](../CMTGatewayAPIFactory.md) / Version

[Previous](LicenseCheck.md) | [Next](../Main-Interface.md)

# CMTGatewayAPIFactory::Version

Get the version of the loaded Gateway API library.

C++
    
    
    MTAPIRES  CMTGatewayAPIFactory::Version(
       UINT&     version   // Gateway API version
       )

.NET
    
    
    MTRetCode SMTGatewayAPIFactory.GetVersion(
       out uint  version   // Gateway API version
       )

### Parameters

**version**  
[in] The version of the loaded Gateway API library.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='event-interface-hookgatewayaccountrequest-md'></a>
### 195. `Event-Interface/HookGatewayAccountRequest.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / HookGatewayAccountRequest

[Previous](HookGatewayOrdersRequest.md) | [Next](../../Report-API/README.md)

# IMTGatewaySink::HookGatewayAccountRequest

The hook for synchronizing MetaTrader 5 client's trading data with an external trading system. The hook is called when clicking "Synchronize" at "Account" tab of MetaTrader 5 Administrator, as well as when calling IMTAdminAPI::UserExternalSync and IMTManagerAPI::UserExternalSync methods from MetaTrader 5 Manager API.

When calling the hook, the gateway developer should decide whether orders, positions and client balance from an external system should be requested. Depending on the decision, one of [response codes](../../Return-Codes/Successful-completion.md) should be returned from the hook:

  * MT_RET_OK — if this code is returned, the developer is to call [IMTGatewayAPI::GatewayAccountAnswer](../Main-Interface/Synchronizing-Trading-Data/GatewayAccountAnswer.md) method that will be used to pass the response code for receiving data from an external system (MT_RET_OK) and the data itself, if it is received successfully. After that, the passed orders, positions and balance replace the same data for the specified client account.
  * MT_RET_OK_NONE — if this code is returned, the gateway developer signalizes that the current orders, positions and client balance have already been synchronized with an external system, the new synchronization does not happen.



C++
    
    
    MTAPIRES  IMTGatewaySink::HookGatewayAccountRequest(
       UINT64         login,       // Login
       LPCWSTR        account_id   // Account number in an external system
       )

.NET
    
    
    MTRetCode  CIMTGatewaySink.HookGatewayAccountRequest(
       ulong          login,       // Login
       srting         account_id   // Account number in an external system
       )

### Parameters

**login**  
[in] Account login, for which synchronization is performed.

***account_id**  
[in] ID of the client's external trading system account, for which synchronization is performed.

### Return Value

MT_RET_OK or MT_RET_OK_NONE response code depending on whether the data is synchronized. In case of an error, the appropriate [error code](../../Return-Codes/README.md) should be returned.

```

---

<a id='event-interface-hookgatewayordersrequest-md'></a>
### 195. `Event-Interface/HookGatewayOrdersRequest.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / HookGatewayOrdersRequest

[Previous](HookGatewayPositionsCheck.md) | [Next](HookGatewayAccountRequest.md)

# IMTGatewaySink::HookGatewayOrdersRequest

The hook for receiving the state of the client's current pending orders in an external trading system.

The functionality is currently under development.  
---  
  
When calling the hook, the gateway developer should decide whether orders from an external system should be requested. Depending on the decision, one of [response codes](../../Return-Codes/Successful-completion.md) should be returned from the hook:

  * MT_RET_OK — if this code is returned, the developer is to call [IMTGatewayAPI::GatewayOrdersAnswer](../Main-Interface/Controlling-Orders-in-External-System/GatewayOrdersAnswer.md) method that will be used to pass the response code for receiving orders from an external system (MT_RET_OK) and the orders themselves, if it is received successfully.
  * MT_RET_OK_NONE — if this code is returned, the gateway developer signalizes that the current orders have already been passed to MetaTrader 5 using [IMTGatewayAPI::GatewayOrdersAnswer](../Main-Interface/Controlling-Orders-in-External-System/GatewayOrdersAnswer.md) method.



C++
    
    
    MTAPIRES  IMTGatewaySink::HookGatewayOrdersRequest()

.NET
    
    
    MTRetCode  CIMTGatewaySink.HookGatewayOrdersRequest()

### Return Value

MT_RET_OK or MT_RET_OK_NONE response code depending on the sequence of actions when working with an external system. In case of an error, the appropriate [error code](../../Return-Codes/README.md) should be returned.

```

---

<a id='event-interface-hookgatewaypositionscheck-md'></a>
### 195. `Event-Interface/HookGatewayPositionsCheck.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / HookGatewayPositionsCheck

[Previous](HookGatewayPositionsRequest.md) | [Next](HookGatewayOrdersRequest.md)

# IMTGatewaySink::HookGatewayPositionsCheck

Hook for positions verification. This method is reserved for future use.

C++
    
    
    MTAPIRES  IMTGatewaySink::HookGatewayPositionsCheck()

.NET
    
    
    MTRetCode  CIMTGatewaySink.HookGatewayPositionsCheck()

### Return Value

[Response code](../../Return-Codes/README.md).

```

---

<a id='event-interface-hookgatewaypositionsrequest-md'></a>
### 195. `Event-Interface/HookGatewayPositionsRequest.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / HookGatewayPositionsRequest

[Previous](HookServerConnect.md) | [Next](HookGatewayPositionsCheck.md)

# IMTGatewaySink:: HookGatewayPositionsRequest

The hook for receiving states of trading accounts used by the gateway to operate in an external system. The hook is called when clicking "Request" on "Positions" tab of the gateway in MetaTrader 5 Administrator.

When calling the hook, the gateway developer should decide whether positions from an external system should be requested. Depending on the decision, one of [response codes](../../Return-Codes/Successful-completion.md) should be returned from the hook:

  * MT_RET_OK — if this code is returned, the developer is to call [IMTGatewayAPI::GatewayPositionsAnswer](../Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md) method that will be used to transfer the response code for receiving positions from an external trading system (MT_RET_OK), as well as positions themselves if they are received successfully. After that, the positions will be displayed on "Positions" tab of the gateway in MetaTrader 5 Administrator. Such sequence of actions is used if an external system provides data on positions in real time mode.
  * MT_RET_OK_NONE — if this code is returned, the gateway developer signalizes that positions from an external system have already been transferred to MetaTrader 5 using [IMTGatewayAPI::GatewayPositionsAnswer](../Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md) method. Such sequence of actions is used if an external system provides data on positions only after the end of a trading session (clearing). When launching a gateway or completing a trading session, the developer should receive data on external trading system positions and submit it to Gateway API using [IMTGatewayAPI::GatewayPositionsAnswer](../Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md) method. Further on, MT_RET_OK_NONE response code should be returned when calling HookGatewayPositionsRequest hook before the gateway reset or a trade session end.



C++
    
    
    MTAPIRES  IMTGatewaySink::HookGatewayPositionsRequest()

.NET
    
    
    MTRetCode  CIMTGatewaySink.HookGatewayPositionsRequest()

### Return Value

MT_RET_OK or MT_RET_OK_NONE response code depending on the sequence of actions when working with an external system. In case of an error, the appropriate [error code](../../Return-Codes/README.md) should be returned.

```

---

<a id='event-interface-hookserverconnect-md'></a>
### 195. `Event-Interface/HookServerConnect.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / HookServerConnect

[Previous](OnDealerLock.md) | [Next](HookGatewayPositionsRequest.md)

# IMTGatewaySink::HookServerConnect

The hook for managing MetaTrader 5 platform components connections to Gateway API.

C++
    
    
    virtual MTAPIRES  IMTGatewaySink::HookServerConnect(
       LPCWSTR       address,     // IP address
       const UINT    type,        // Component type
       const UINT64  login        // Login
       )

.NET
    
    
    virtual MTAPIRES  CIMTGatewaySink.HookServerConnect(
       string        address,     // IP address
       uint          type,        // Component type
       ulong         login        // Login
       )

### Parameters

**address**  
[in] IP address, from which a platform component is connected.

**type**  
[in] Type of the platform component that is trying to connect.IMTGatewayAPI::CONNECT_TYPE_TRADE(trading server) andIMTGatewayAPI::CONNECT_TYPE_HISTORY(history server) values are used for passing the type.

**login**  
[in] The login used by a platform component to establish connection.

### Return Value

In case of confirmation [MT_RET_OK](../../Return-Codes/Successful-completion.md) should be returned, otherwise, the request will be rejected with a response code returned from the hook.

### Note

Do not confuse connection login with server ID (IMTConServer::ID). This login is specified in gateway/data feed settings ([IMTConFeeder::Login](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/FeedLogin.md)/[IMTConGateway::Login](../../Configuration-Interfaces/Gateways/IMTConGateway/TradingLogin.md)). The login is always equal to 1000 for local data feeds and gateways.

```

---

<a id='event-interface-ondealeranswer-md'></a>
### 195. `Event-Interface/OnDealerAnswer.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnDealerAnswer

[Previous](OnGatewayAccountAnswer.md) | [Next](OnDealerLock.md)

# IMTGatewaySink::OnDealerAnswer

A handler of the event notifying on a request confirmation result.

C++
    
    
    virtual void  IMTGatewaySink::OnDealerAnswer(
       const MTAPIRES    retcode,      // Result
       const IMTConfirm* confirm       // Request confirmation object
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnDealerAnswer(
       MTRetCode         retcode,      // Result
       CIMTConfirm       confirm       // Request confirmation object
       )

### Parameters

**retcode**  
[in] Request confirmationresult code.MT_RET_OKis returned, in case a request is confirmed successfully.

**confirm**  
[in]Request confirmation object.

# IMTGatewaySink::OnDealerAnswer

A handler of the event notifying on a request execution result.

C++
    
    
    virtual void  IMTGatewaySink::OnDealerAnswer(
       const UINT64        login,        // Server ID
       const MTAPIRES      retcode,      // Result
       const IMTExecution* execution     // Trade execution object
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnDealerAnswer(
       ulong               login,        // Server ID
       MTRetCode           retcode,      // Result
       CIMTExecution       execution     // Trade execution object
       )

### Parameters

**login**  
[in] Identifier of a server that has executed the request.

**retcode**  
[in] Request executionresult code.MT_RET_OKis returned, in case a request is executed successfully.

**execution**  
[in]Trade execution object.

### Note

This event informs about the result of applying a trade execution object [IMTExecution](../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTExecution.md) sent via [IMTGatewayAPI:DealerExecuteAsync](../Main-Interface/Processing-Trade-Requests/DealerExecuteAsync.md) to a trade server data base.

```

---

<a id='event-interface-ondealerlock-md'></a>
### 195. `Event-Interface/OnDealerLock.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnDealerLock

[Previous](OnDealerAnswer.md) | [Next](HookServerConnect.md)

# IMTGatewaySink::OnDealerLock

A handler of the event of capturing (blocking) of a successive trade request from a requests queue.

C++
    
    
    virtual void  IMTGatewaySink::OnDealerLock(
       const MTAPIRES     retcode,       // Result
       const IMTRequest*  request,       // An object of a trade request
       const IMTUser*     user,          // An object of a client record
       const IMTAccount*  account,       // An object of a trading account
       const IMTOrder*    order,         // An order object
       const IMTPosition* position       // Position object
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnDealerLock(
       MTRetCoed          retcode,       // Result
       CIMTRequest        request,       // An object of a trade request
       CIMTUser           user,          // An object of a client record
       CIMTAccount        account,       // An object of a trading account
       CIMTOrder          order,         // An order object
       CIMTPosition       position       // Position object
       )

### Parameters

**retcode**  
[in] Trading request captureresult code.MT_RET_OKis returned, in case of a successful capture. Code MT_RET_OK_NONE means that the request is no longer available on the trade server. For example, it could have been captured by another dealer or application.

**request**  
[in] Capturedtrade request object.

**user**  
[in]Client record objectwho formed a request.

**account**  
[in]Trading account objectof the client who formed a request.

**order**  
[in]Object of the orderthat corresponds to a request.

**position**  
[in] Clientposition objectby the request instrument before its execution.

### Note

The method is used only for gateways.

```

---

<a id='event-interface-ongatewayaccountanswer-md'></a>
### 195. `Event-Interface/OnGatewayAccountAnswer.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnGatewayAccountAnswer

[Previous](OnGatewayAccountSet.md) | [Next](OnDealerAnswer.md)

# IMTGatewaySink::OnGatewayAccountAnswer

This is a handler for an event of receiving a result of a request for MetaTrader 5 platform user data. This handler receives a user data requested via [IMTGatewayAPI::GatewayAccountRequest](../Main-Interface/Synchronizing-Trading-Data/GatewayAccountRequest.md) method.

C++
    
    
    virtual void  IMTGatewaySink::OnGatewayAccountAnswer(
       const MTAPIRES          retcode,          // Result
       const INT64             request_id,       // Request ID
       const IMTUser*          user              // An object of a client record
       const IMTAccount*       account           // An object of a trading account
       const IMTOrderArray*    orders            // Array of orders
       const IMTPositionArray* positions         // Positions array
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnGatewayAccountAnswer(
       MTRetCode               retcode,          // Result
       long                    request_id,       // Request ID
       CIMTUser                user              // An object of a client record
       CIMTAccount             account           // An object of a trading account
       CIMTOrderArray          orders            // Array of orders
       CIMTPositionArray       positions         // Positions array
       )

### Parameters

**retcode**  
[in] Code of the data request processing result. MT_RET_OK response code is returned if the data has been successfully received. Otherwise, the appropriateerror codeis returned.

**request_id**  
[in] Request ID. It is used for binding the requests executed byIMTGatewayAPI::GatewayAccountRequestmethod and the answers received via this handler.

***user**  
[in]An object of the client record. OnlyLoginfield and a client account number in an external trading system are passed in IMTUser objectIMTUser::ExternalAccountGetmethod should be used to receive a client account number).

***account**  
[in]Trading account object. OnlyBalancefield is used in IMTAccount object for passing the actual balance value.

***orders**  
[in]An object of the array ofclient orders.

***positions**  
[in]An object of the array ofclient positions.

### 

```

---

<a id='event-interface-ongatewayaccountset-md'></a>
### 195. `Event-Interface/OnGatewayAccountSet.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnGatewayAccountSet

[Previous](OnGatewayShutdown.md) | [Next](OnGatewayAccountAnswer.md)

# IMTGatewayAPI::OnGatewayAccountSet

This handler receives [IMTGatewayAPI::GatewayAccountSet](../Main-Interface/Synchronizing-Trading-Data/GatewayAccountSet.md) method execution result, as well as the final status of a client entry (after the passed changes have been applied).

C++
    
    
    MTAPIRES  IMTGatewayAPI::OnGatewayAccountSet(
       const MTAPIRES          retcode,          // Result
       const INT64             request_id        // Request ID
       const IMTUser*          user              // An object of a client record
       const IMTAccount*       account           // An object of a trading account
       const IMTOrderArray*    orders            // Array of orders
       const IMTPositionArray* positions         // Positions array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.OnGatewayAccountSet(
       MTRetCode               retcode,          // Result
       long                    request_id        // Request ID
       CIMTUser                user              // An object of a client record
       CIMTAccount             account           // An object of a trading account
       CIMTOrderArray          orders            // Array of orders
       CIMTPositionArray       positions         // Positions array
       )

### Parameters

**retcode**  
[in]IMTGatewayAPI::GatewayAccountSetexecution result code. MT_RET_OK response code is passed if a client entry has been successfully changed. Otherwise, the appropriateerror codeis returned.

**request_id**  
[in] Arbitrary request ID. It is used for binding the requests executed byIMTGatewayAPI::GatewayAccountSetmethod and the answers received via this handler.

**user**  
[in]An object of the client record.Loginfield is used in IMTUser object for identifying a user, whose data has been changed. The client external system's account number corresponding to the gateway can also be used for identification. Account in an external system can be defined usingIMTUser::ExternalAccountAddmethod.

**account**  
[in]Trading account object. OnlyBalancefield is used in IMTAccount object for passing the balance value.

**orders**  
[in]An object of the array of ordersplaced for the specified account.

**positions**  
[in]An object of the array of positionsplaced for the specified account.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

After a client's data is changed using [IMTGatewayAPI::GatewayAccountSet](../Main-Interface/Synchronizing-Trading-Data/GatewayAccountSet.md) method, the status of the client's trading account, orders and positions is passed to account, orders and positions parameters.

```

---

<a id='event-interface-ongatewayconfig-md'></a>
### 195. `Event-Interface/OnGatewayConfig.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnGatewayConfig

[Previous](OnServerSymbolDelete.md) | [Next](OnGatewayStart.md)

# IMTGatewaySink::OnGatewayConfig

A handler of the event of passing a gateway own configuration from a history server connected to it.

C++
    
    
    virtual void  IMTGatewaySink::OnGatewayConfig(
       const UINT64         login,       // Login
       const IMTConGateway* config      // Gateway configuration object
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnGatewayConfig(
       ulong                login,       // Login
       CIMTConGateway       config      // Gateway configuration object
       )

### Parameters

**login**  
[in] The login, from which a platform component was connected.

***config**  
[in]The gateway configuration object.

### Note

During the connection a history server passes the gateway settings specified in the platform for it.

  * The symbol settings should not contain the source ([IMTConSymbol::Source](../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md)). Otherwise, the quotes are copied from it.
  * Receiving quotes from data sources ([IMTConSymbol::TICK_REALTIME (#entickflags)](../../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags)) should be enabled in the symbol settings. Otherwise, only quotes thrown in by dealers via the Manager terminals are accepted.
  * The "Quotes" or "Quotes and News" mode ([IMTConFeeder::FEED_FLAG_QUOTES (#enfeedersmode)](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/Enumerations.md#enfeedersmode)) should be used for a data feed. Otherwise, the data feed quotes are rejected.



# IMTGatewaySink::OnGatewayConfig

A handler of the event of passing a data feed own configuration from a history server connected to it.

C++
    
    
    virtual void  IMTGatewaySink::OnGatewayConfig(
       const UINT64        login,       // Login
       const IMTConFeeder* config       // Data feed configuration object
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnGatewayConfig(
       ulong               login,       // Login
       CIMTConFeeder       config       // Data feed configuration object
       )

### Parameters

**login**  
[in] The login, from which a platform component was connected.

***config**  
[in]Data feed configuration object.

### Note

History servers of different MetaTrader 5 trading platforms can connect to the same data feed. During the connection a history server passes the data feed settings specified in the platform for it.

  * The symbol settings should not contain the source ([IMTConSymbol::Source](../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md)). Otherwise, the quotes are copied from it.
  * Receiving quotes from data sources ([IMTConSymbol::TICK_REALTIME (#entickflags)](../../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags)) should be enabled in the symbol settings. Otherwise, only quotes thrown in by dealers via the Manager terminals are accepted.
  * The "Trade and Quote" mode (the [IMTConGateway::GATEWAY_FLAG_IGNORE_QUOTES (#engatewaymode)](../../Configuration-Interfaces/Gateways/IMTConGateway/Enumerations.md#engatewaymode) flag is not enabled) should be used for a gateway. Otherwise, the gateway quotes are rejected.



```

---

<a id='event-interface-ongatewayshutdown-md'></a>
### 195. `Event-Interface/OnGatewayShutdown.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnGatewayShutdown

[Previous](OnGatewayStop.md) | [Next](OnGatewayAccountSet.md)

# IMTGatewaySink::OnGatewayShutdown

A handler of the event notifying about the trading platform shutdown or gateway/data feed disconnection.

C++
    
    
    virtual void  IMTGatewaySink::OnGatewayShutdown(
       const UINT64  login      // Login
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnGatewayShutdown(
       ulong         login      // Login
       )

### Parameters

**login**  
[in] Login of the platform component from which the shutdown event has been received.

### Note

This event allows the programmer to gracefully terminate the gateway/datafeed. After receiving the event, the application must stop operation; otherwise, the process will be stopped forcibly after 5 seconds.

```

---

<a id='event-interface-ongatewaystart-md'></a>
### 195. `Event-Interface/OnGatewayStart.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnGatewayStart

[Previous](OnGatewayConfig.md) | [Next](OnGatewayStop.md)

# IMTGatewaySink::OnGatewayStart

A handler of the following event: Gateway API is [synchronized](../Interaction-of-the-Platform-and.md) with the platform and is ready for work.

C++
    
    
    virtual void  IMTGatewaySink::OnGatewayStart()

.NET
    
    
    virtual void  CIMTGatewaySink.OnGatewayStart()

### Note

Gateway API business logic elements methods (adding of [symbols](../Main-Interface/Configuration-Databases/Symbols.md), connection as a [dealer](../Main-Interface/Processing-Trade-Requests.md), etc.).

```

---

<a id='event-interface-ongatewaystop-md'></a>
### 195. `Event-Interface/OnGatewayStop.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnGatewayStop

[Previous](OnGatewayStart.md) | [Next](OnGatewayShutdown.md)

# IMTGatewaySink::OnGatewayStop

[IMTGatewaySink::OnGatewayStart](OnGatewayStart.md) inverse events handler. The notification is on the fact that Gateway API is not synchronized with the platform and not ready for work.

C++
    
    
    virtual void  IMTGatewaySink::OnGatewayStop()

.NET
    
    
    virtual void  CIMTGatewaySink.OnGatewayStop()

### Note

This notification is sent for gateways, in case of the failure of the connection to a main trading or historical server.

```

---

<a id='event-interface-onserverdisconnect-md'></a>
### 195. `Event-Interface/OnServerDisconnect.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnServerDisconnect

[Previous](../Event-Interface.md) | [Next](OnServerSynchronized.md)

# IMTGatewaySink::OnServerDisconnect

A handler of the event of the end of connection to one of the MetaTrader 5 platform components (server).

C++
    
    
    virtual void  IMTGatewaySink::OnServerDisconnect(
       LPCWSTR       address,     // IP address
       const UINT    type,        // Component type
       const UINT64  login        // Login
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnServerDisconnect(
       string        address,     // IP address
       uint          type,        // Component type
       ulong         login        // Login
       )

### Parameters

**address**  
[in] IP address, from which a platform component was connected.

**type**  
[in] Type of the platform component that was connected.IMTGatewayAPI::CONNECT_TYPE_TRADE(trading server) andIMTGatewayAPI::CONNECT_TYPE_HISTORY(history server) values are used for passing the type.

**login**  
[in] The login, from which a platform component was connected.

### Note

Do not confuse connection login with server ID (IMTConServer::ID). This login is specified in gateway/data feed settings ([IMTConFeeder::Login](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/FeedLogin.md)/[IMTConGateway::Login](../../Configuration-Interfaces/Gateways/IMTConGateway/TradingLogin.md)). The login is always equal to 1000 for local data feeds and gateways.

```

---

<a id='event-interface-onserversymboladd-md'></a>
### 195. `Event-Interface/OnServerSymbolAdd.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnServerSymbolAdd

[Previous](OnServerSynchronized.md) | [Next](OnServerSymbolDelete.md)

# IMTGatewaySink::OnServerSymbolAdd

A handler of the event of adding a new symbol.

C++
    
    
    virtual void  IMTGatewaySink::OnServerSymbolAdd(
       LPCWSTR              symbol      // The name of the added symbol
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnServerSymbolAdd(
       string               symbol      // The name of the added symbol
       )

### Parameters

**symbol**  
[in] The name of the added symbol.

### Note

This method is called by the Gateway API to notify that a new symbol has been added.

  * If translation is not configured for the added symbol, the original name of the symbol used in the platform will be passed.
  * If translation is configured for the added symbol, the name of the source symbol is passed in 'symbol'.
  * The IMTGatewaySink::OnServerSymbolAdd method is only called if there were no symbols with the same Source ([IMTConGatewayTranslate::Source](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate/Source.md)) specified in translation parameters in the platform before. Consider the following example: the platform has no EURUSD symbol, but it is set as the source in the gateway translation settings. In this case, the gateway will not receive the OnServerSymbolAdd event after adding EURUSD in the platform. The event is not required, since the gateway knows about the need to feed EURUSD quotes through a synonymous symbol.


  * The symbol settings should not contain the source ([IMTConSymbol::Source](../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md)). Otherwise, the quotes are copied from it.
  * Receiving quotes from data sources ([IMTConSymbol::TICK_REALTIME (#entickflags)](../../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags)) should be enabled in the symbol settings. Otherwise, only quotes thrown in by dealers via the Manager terminals are accepted.
  * The "Quotes" or "Quotes and News" mode ([IMTConFeeder::FEED_FLAG_QUOTES (#enfeedersmode)](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/Enumerations.md#enfeedersmode)) should be used for a data feed. Otherwise, the data feed quotes are rejected.


  * The "Trade and Quote" mode (the [IMTConGateway::GATEWAY_FLAG_IGNORE_QUOTES (#engatewaymode)](../../Configuration-Interfaces/Gateways/IMTConGateway/Enumerations.md#engatewaymode) flag is not enabled) should be used for a gateway. Otherwise, the gateway quotes are rejected.



```

---

<a id='event-interface-onserversymboldelete-md'></a>
### 195. `Event-Interface/OnServerSymbolDelete.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnServerSymbolDelete

[Previous](OnServerSymbolAdd.md) | [Next](OnGatewayConfig.md)

# IMTGatewaySink::OnServerSymbolDelete

A handler of the event of symbol removal.

C++
    
    
    virtual void  IMTGatewaySink::OnServerSymbolDelete(
       LPCWSTR              symbol      // The name of the deleted symbol
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnServerSymbolDelete(
       string               symbol      // The name of the deleted symbol
       )

### Parameters

**config**  
[in] The name of the deleted symbol

### Note

This method is called by the Gateway API to notify the gateway/data feed that a new symbol has been added.

  * If translation is not configured for the deleted symbol, the original name of the symbol used in the platform will be passed.
  * If translation is configured for the deleted symbol, the name of the source symbol is passed in 'symbol'.
  * The IMTGatewaySink::OnServerSymbolDelete method is only called if there are no symbols with the same Source specified in translation settings left in the platform. Consider the following example, 2 symbols are specified in translation settings. EURUSD.1 and EURUSD.2. The two symbols use the same source EURUSD ([IMTConGatewayTranslate::Source](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate/Source.md)). In this case, the gateway will not receive a notification of OnServerSymbolDelete, until both symbols EURUSD.1 and EURUSD.2 are deleted.


  * The symbol settings should not contain the source ([IMTConSymbol::Source](../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md)). Otherwise, the quotes are copied from it.
  * Receiving quotes from data sources ([IMTConSymbol::TICK_REALTIME (#entickflags)](../../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags)) should be enabled in the symbol settings. Otherwise, only quotes thrown in by dealers via the Manager terminals are accepted.
  * The "Quotes" or "Quotes and News" mode ([IMTConFeeder::FEED_FLAG_QUOTES (#enfeedersmode)](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/Enumerations.md#enfeedersmode)) should be used for a data feed. Otherwise, the data feed quotes are rejected.


  * The "Trade and Quote" mode (the [IMTConGateway::GATEWAY_FLAG_IGNORE_QUOTES (#engatewaymode)](../../Configuration-Interfaces/Gateways/IMTConGateway/Enumerations.md#engatewaymode) flag is not enabled) should be used for a gateway. Otherwise, the gateway quotes are rejected.



```

---

<a id='event-interface-onserversynchronized-md'></a>
### 195. `Event-Interface/OnServerSynchronized.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Event Interface](../Event-Interface.md) / OnServerSynchronized

[Previous](OnServerDisconnect.md) | [Next](OnServerSymbolAdd.md)

# IMTGatewaySink::OnServerSynchronized

A handler of the event of data synchronization between Gateway API and one of the MetaTrader 5 platform (server) components.

C++
    
    
    virtual void  IMTGatewaySink::OnServerSynchronized(
       LPCWSTR       address,     // IP address
       const UINT    type,        // component type
       const UINT64  id           // server ID
       )

.NET
    
    
    virtual void  CIMTGatewaySink.OnServerSynchronized(
       string        address,     // IP address
       uint          type,        // component type
       ulong         id           // server ID
       )

### Parameters

**address**  
[in] IP address of the platform component the synchronization has been performed with.

**type**  
[in] Type of the platform component the synchronization has been performed with. TheIMTGatewayAPI::CONNECT_TYPE_TRADE(trade server),IMTGatewayAPI::CONNECT_TYPE_HISTORY(history server) andIMTGatewayAPI::CONNECT_TYPE_BACKUP(backup server) values are used to pass the type.

**id**  
[in] ID of the server (IMTConServer::ID) the synchronization has been performed with. This parameter passes 0 when synchronizing with the history or backup server.

### Note

Use this handler if the gateway works with additional (not main) trade servers. When working only with the main trade server, it is sufficient to use [IMTGatewaySink::OnGatewayStart](OnGatewayStart.md).

```

---

<a id='exported-functions-mtgatewaycreate-md'></a>
### 195. `Exported-Functions/MTGatewayCreate.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Exported Functions](../Exported-Functions.md) / MTGatewayCreate

[Previous](MTGatewayVersion.md) | [Next](MTGatewayCreateLocal.md)

# MTGatewayCreate

MTGatewayCreate exported function creates a new [IMTGatewayAPI](../Main-Interface.md) interface copy and returns a pointer to it.
    
    
    MTAPIRES  MTGatewayCreate(
       MTGatewayInfo&   info      // Reference to MTGatewayInfo
       IMTGatewayAPI**  gateway   // Pointer to a pointer o the interface
       )

### Parameters

**info**  
[out] A reference to theMTGatewayInfostructure.

**gateway**  
[out] A pointer to a pointer to the createdIMTGatewayAPIinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='exported-functions-mtgatewaycreatelocal-md'></a>
### 195. `Exported-Functions/MTGatewayCreateLocal.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Exported Functions](../Exported-Functions.md) / MTGatewayCreateLocal

[Previous](MTGatewayCreate.md) | [Next](../CMTGatewayAPIFactory.md)

# MTGatewayCreateLocal

MTGatewayCreateLocal exported function creates a new [IMTGatewayAPI](../Main-Interface.md) interface copy with predetermined parameters submitted in the command line and returns a pointer to it.
    
    
    MTAPIRES  MTGatewayCreate(
       MTGatewayInfo&   info      // Reference to MTGatewayInfo
       IMTGatewayAPI**  gateway   // Pointer to a pointer o the interface
       int              argc      // Number of command line parameters
       wchar_t**        argv      // Command line parameters
       )

### Parameters

**info**  
[out] A reference to theMTGatewayInfostructure.

**gateway**  
[out] A pointer to a pointer to the createdIMTGatewayAPIinterface.

**argc**  
[in] Number ofcommand line parameters.

**argv**  
[in]Parameters of the command linethat launched the gateway/data feed.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

This function type is called instead of [MTGatewayCreate](MTGatewayCreate.md), in case additional parameters were indicated in a command line during the run of a gateway/data feed executable file. Parameters of the command line are passed to the argc and argv parameters. The following additional running parameters are possible:

  * /name:XXX — the name of the gateway/data feed that will be used for the folder, in which the application data (like operation logs) will be stored. This folder is created in the directory where the executable file of the gateway/data feed is located.
  * /address:XXX — the default address on which the server port GatewayAPI runs;
  * /login:XXX — the default login that will be used for connecting history and trade servers to a gateway/data feed.
  * /password:XXX — the default password that will be used for connecting history and trade servers to a gateway/data feed.
  * /timezone:XXX — time zone in minutes (for example, GMT +01:00 corresponds to 60, GMT -01:00 corresponds to -60), that will be used in gateway/data feed settings.
  * /timecorrect — if this parameter is used, DST adjustment is enabled.
  * /standalone — when this flag is enabled, the [IMTGatewaySink::OnGatewayShutdown](../Event-Interface/OnGatewayShutdown.md) event handler, which notifies of trading platform shutdown, will not be called.
  * /description — the history server runs a gateway/data feed with this parameter, when it is required to get the description of the gateway/data feed module. The description is used for including the module in the list of available gateways/data feeds when creating/modifying the corresponding configuration via MetaTrader 5 Administrator. In addition, the description is used for convenient managing the gateway/data feed settings via MetaTrader 5 Administrator — this description determines modes of the gateway/data feed operation, its default setting, etc. The description represents a [MTGatewayInfo](../../Structures/MTGatewayInfo.md) structure.



> The address, on which the gateway/data feed runs, and the parameters of the account for connecting to it are provided to facilitate application debugging.

```

---

<a id='exported-functions-mtgatewayversion-md'></a>
### 195. `Exported-Functions/MTGatewayVersion.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Exported Functions](../Exported-Functions.md) / MTGatewayVersion

[Previous](../Exported-Functions.md) | [Next](MTGatewayCreate.md)

# MTGatewayVersion

MTGatewayVersion exported function returns Gateway API library version.
    
    
    MTAPIRES  MTGatewayVersion(
       UINT&  version      // Reference to a Gateway API version
       )

### Parameters

**version**  
[in] A reference to a Gateway API version.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='main-interface-client-connection-md'></a>
### 195. `Main-Interface/Client-Connection.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Client Connection

[Previous](External-Connection-State/StateTraffic.md) | [Next](Client-Connection/ClientAdd.md)

# Client Connection

The functions described in this section provide control of connections to gateways/data feeds using logins, passwords and IP-addresses.

The following functions are provided:

Function | Purpose  
---|---  
[ClientAdd](Client-Connection/ClientAdd.md) | Adding permission for the platform components connection using a specified login and a password.  
[ClientAllowIP](Client-Connection/ClientAllowIP.md) | Adding permission for the connection from a specified IP address.

```

---

<a id='main-interface-common-functions-md'></a>
### 195. `Main-Interface/Common-Functions.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Common Functions

[Previous](Enumerations.md) | [Next](Common-Functions/Allocate.md)

# Common Functions

The common functions of the MetaTrader 5 Gateway API include general purpose functions that do not manage any of the settings or data but are required for writing a gateway.

## Memory Management

The MetaTrader 5 Gateway API allows managing the memory used by applications.

Function | Purpose  
---|---  
[Allocate](Common-Functions/Allocate.md) | Memory allocation by an application.  
[Free](Common-Functions/Free.md) | Free memory allocated previously using the Allocate method.  
  
## Journal

MetaTrader 5 Report API provides access to server logs allowing to output records in them and save that records on the hard drive.

Function | Purpose  
---|---  
[LoggerOut](Common-Functions/LoggerOut.md) | Log messages.  
[LoggerOutString](Common-Functions/LoggerOutString.md) | Quick output of unformatted stings to the journal.  
[LoggerFlush](Common-Functions/LoggerFlush.md) | Flush the file buffer of the journal to a disk.  
  
## Service Functions

The following additional functions are available in the MetaTrader 5 Gateway API:

Function | Purpose  
---|---  
[Release](Common-Functions/Release.md) | Delete an object.  
[LicenseCheck](Common-Functions/LicenseCheck.md) | A function for checking the gateway/data feed usage license.

```

---

<a id='main-interface-configuration-databases-md'></a>
### 195. `Main-Interface/Configuration-Databases.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Configuration Databases

[Previous](Users/UserLogins.md) | [Next](Configuration-Databases/Common.md)

# Configuration Databases

MetaTrader 5 Gateway API functions allow to work with different platform configurations. Possibility to import symbols is also provided in Gateway API together with getting configuration data necessary for gateways operation and data feeds.

  * [Common](Configuration-Databases/Common.md)
  * [Data Feeds](Configuration-Databases/Data-Feeds.md)
  * [Gateways](Configuration-Databases/Gateways.md)
  * [Symbols](Configuration-Databases/Symbols.md)
  * [Groups](Configuration-Databases/Groups.md)
  * [Time](Configuration-Databases/Time.md)
  * [Network](Configuration-Databases/Network.md)
  * [Spreads](Configuration-Databases/Spreads.md)



```

---

<a id='main-interface-controlling-orders-in-external-system-md'></a>
### 195. `Main-Interface/Controlling-Orders-in-External-System.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Controlling Orders in External System

[Previous](Controlling-Positions-in-External-System/GatewayPositionsCheck.md) | [Next](Controlling-Orders-in-External-System/GatewayOrderArrayCreate.md)

# Controlling Orders in External System

MetaTrader 5 Gateway API provides possibility to control the state of the client's current pending orders placed in an external system.

The functionality is currently under development.  
---  
  
Functions | Purpose  
---|---  
[GatewayOrderArrayCreate](Controlling-Orders-in-External-System/GatewayOrderArrayCreate.md) | Create an object of the array of orders.  
[GatewayOrdersAnswer](Controlling-Orders-in-External-System/GatewayOrdersAnswer.md) | Display the client's current pending orders placed in an external system.

```

---

<a id='main-interface-controlling-positions-in-external-system-md'></a>
### 195. `Main-Interface/Controlling-Positions-in-External-System.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Controlling Positions in External System

[Previous](Processing-Trade-Requests/DealerExecuteAsync.md) | [Next](Controlling-Positions-in-External-System/GatewayParamArrayCreate.md)

# Controlling Positions in External System

MetaTrader 5 Gateway API provides possibility to control position states of the trading accounts, at which the gateway operates in an external system.

If the gateway has such a functionality, the platform administrator can request the state of positions on the trading accounts in an external system via MetaTrader 5 Administrator. The special tab is provided for that:

![Requesting positions in an external trading system](images/gateway_positions.png)

When clicking "Request", [IMTGatewaySink::HookGatewayPositionsRequest](../Event-Interface/HookGatewayPositionsRequest.md) hook is called in Gateway API. Positions are received and displayed using the hook and the functions described in this section.

Functions | Purpose  
---|---  
[GatewayParamArrayCreate](Controlling-Positions-in-External-System/GatewayParamArrayCreate.md) | Create an object of the array of parameters.  
[GatewayPositionArrayCreate](Controlling-Positions-in-External-System/GatewayPositionArrayCreate.md) | Create an object of the array of positions.  
[GatewayPositionsAnswer](Controlling-Positions-in-External-System/GatewayPositionsAnswer.md) | Display positions on external trading system accounts in MetaTrader 5 Administrator.  
[GatewayPositionsCheck](Controlling-Positions-in-External-System/GatewayPositionsCheck.md) | Verify positions. This method is reserved for future use.

```

---

<a id='main-interface-enumerations-md'></a>
### 195. `Main-Interface/Enumerations.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Enumerations

[Previous](../Main-Interface.md) | [Next](Common-Functions.md)

<a id="enumerations"></a>
# Enumerations (#enumerations)

The following enumerations are provided in the IMTGatewayAPI interface:

  * [IMTGatewayAPI::EnDealerRequestFlags (#endealerrequestflags)](Enumerations.md#endealerrequestflags)
  * [IMTGatewayAPI::EnConnectType (#enconnecttype)](Enumerations.md#enconnecttype)



<a id="endealerrequestflags"></a>
## IMTGatewayAPI::EnDealerRequestFlags (#endealerrequestflags)

The flags describing additional options for a gateway connection as a dealer are listed in IMTGatewayAPI::EnDealerRequestFlags:

ID | Value | Description  
DEALER_FLAG_NONE | 0x00000000 | No additional connection flags.  
DEALER_FLAG_AUTOLOCK | 0x00000001 | Capture new requests from the queue automatically.  
DEALER_FLAG_USER | 0x00000002 | Additionally, get the data on the user who sent a request. In case this flag is turned on, users data will be transferred to the const IMTUser *user parameter of the following methods:

  * [IMTGatewaySink::OnDealerLock](../Event-Interface/OnDealerLock.md)
  * [IMTGatewayAPI::RequestNext](Trade-Requests/RequestNext.md)
  * [IMTGatewayAPI::RequestGet](Trade-Requests/RequestGet.md)

  
DEALER_FLAG_ACCOUNT | 0x00000004 | Additionally, get trading account data of the user who sent a request. In case this flag is turned on, trading account data will be transferred to the const IMTAccount *account parameter of the following methods:

  * [IMTGatewaySink::OnDealerLock](../Event-Interface/OnDealerLock.md)
  * [IMTGatewayAPI::RequestNext](Trade-Requests/RequestNext.md)
  * [IMTGatewayAPI::RequestGet](Trade-Requests/RequestGet.md)

  
DEALER_FLAG_ORDER | 0x00000008 | Additionally, get the data on the order that corresponds to the submitted request. In case this flag is turned on, the data on the order will be transferred to the const IMTOrder *order parameter of the following methods:

  * [IMTGatewaySink::OnDealerLock](../Event-Interface/OnDealerLock.md)
  * [IMTGatewayAPI::RequestNext](Trade-Requests/RequestNext.md)
  * [IMTGatewayAPI::RequestGet](Trade-Requests/RequestGet.md)

Note:

  * Actual prices in the platform are specified in the 'order' parameter without regard to translation parameters ([IMTConGatewayTranslate](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate.md)) set for the gateway.


  * An order is created in the platform for the execution of most requests. For example, to execute a position closing request, an order is created and the execution of the order will close the position. The order data is written to the 'order' parameter of the specified methods along with the request data. Similar behavior is used for triggered SL/TP levels, Stop Out etc. However, for [IMTRequest::TA_SLTP (#ta-sltp)](../../Database-Interfaces/Trade/Trade-Requests/IMTRequest/Requests-Enumerations.md#ta-sltp) requests, the 'order' parameter is not filled even if DEALER_FLAG_ORDER is enabled, since no order is created in the platform in this case.

  
DEALER_FLAG_POSITION | 0x00000010 | Additionally, get a user position data by the request symbol before its execution. In case this flag is turned on, a user position data will be transferred to the const IMTPosition *position parameter of the following methods:

  * [IMTGatewaySink::OnDealerLock](../Event-Interface/OnDealerLock.md)
  * [IMTGatewayAPI::RequestNext](Trade-Requests/RequestNext.md)
  * [IMTGatewayAPI::RequestGet](Trade-Requests/RequestGet.md)

Note: Actual prices in the platform are specified in the 'position' parameter without regard to translation parameters ([IMTConGatewayTranslate](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate.md)) set for the gateway.  
DEALER_FLAG_EXTERNAL_ACC | 0x00000020 | Additionally get information about the account number of a client in an external trade system. In case this flag is turned on, the information about the account is filled in the [IMTRequest](../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequest.md) object that is passed as a parameter by the following functions:

  * [IMTGatewaySink::OnDealerLock](../Event-Interface/OnDealerLock.md)
  * [IMTGatewayAPI::RequestNext](Trade-Requests/RequestNext.md)
  * [IMTGatewayAPI::RequestGet](Trade-Requests/RequestGet.md)

  
DEALER_FLAG_MARKUP_TRADES | 0x00000040 | This flag allows automatic conversion of prices of trade operations when passing the prices from the gateway side into the MetaTrader 5 and back at the Gateway API level in accordance with the settings of [IMTConGatewayTranslate::BidMarkup](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate/BidMarkup.md) and [IMTConGatewayTranslate::AskMarkup](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate/AskMarkup.md). Prices of the quoting flow (including the Depth of Market) are always converted in accordance with the IMTConGatewayTranslate::BidMarkup and IMTConGatewayTranslate::AskMarkup settings.  
  
This enumeration is used in the [IMTGatewayAPI::DealerStart](Processing-Trade-Requests/DealerStart.md) method.

<a id="enconnecttype"></a>
## IMTGatewayAPI::EnConnectType (#enconnecttype)

IMTGatewayAPI::EnConnectType lists the types of platform components.

ID | Value | Purpose  
CONNECT_TYPE_TRADE | 1 | Trade server.  
CONNECT_TYPE_HISTORY | 2 | History server.  
CONNECT_TYPE_ECN | 3 | Access server.  
CONNECT_TYPE_BACKUP | 4 | Backup server.  
  
The enumeration is used in the following methods:

  * [IMTGatewaySink::OnServerDisconnect](../Event-Interface/OnServerDisconnect.md)
  * [IMTGatewaySink::OnServerSynchronized](../Event-Interface/OnServerSynchronized.md)
  * [IMTGatewaySink::HookServerConnect ](../Event-Interface/HookServerConnect.md)



```

---

<a id='main-interface-external-connection-state-md'></a>
### 195. `Main-Interface/External-Connection-State.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / External Connection State

[Previous](Server/Connections.md) | [Next](External-Connection-State/StateConnect.md)

# External Connection Status

The implementation of the gateway/data feed connection to external systems, as well as the relevant connection management, is entirely the responsibility of the application developer. The Gateway API does not provide any specialized methods for this. However, it allows you to implement certain interaction with the end user:

  * Receive and use custom settings for reconnecting to an external server in case of connection loss
  * Display connection status and traffic



Gateway and data feed configurations provide settings for reconnecting in case of connection loss. The settings affect the logic of reconnecting cluster servers to gateways/data feeds (local and remote), but you can also use them to work with an external connection.

![Data feed reconnection settings](images/datafeed_timeouts.png)

The settings can be obtained using the following methods:

  * [IMTConGateway::TimeoutReconnect](../../Configuration-Interfaces/Gateways/IMTConGateway/TimeoutReconnect.md) — time period between attempts to reconnect the gateway to an external server.
  * [IMTConGateway::TimeoutAttempts](../../Configuration-Interfaces/Gateways/IMTConGateway/TimeoutAttempts.md) — the number of attempts in a series of gateway reconnections to an external server.
  * [IMTConGateway::TimeoutSleep](../../Configuration-Interfaces/Gateways/IMTConGateway/TimeoutSleep.md) — time period between series of gateway reconnections to an external server.
  * [IMTConFeeder::TimeoutReconnect](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/TimeoutReconnect.md) — time period between attempts to reconnect the data feed to an external server.
  * [IMTConFeeder::TimeoutAttempts](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/TimeoutAttempts.md) — the number of attempts in a series of data feed reconnections to an external server.
  * [IMTConFeeder::TimeoutSleep](../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/TimeoutSleep.md) — time period between series of data feed reconnections to an external server.



They are described in detail in the "[Interaction with Quote Provider](https://support.metaquotes.net/ru/docs/mt5/platform/components/history_server/history_server_datafeeds)" section of the MetaTrader 5 Administrator Help. You can implement similar logic for reconnecting to an external server in your app.

Status of gateway/data feed connection to external servers is displayed in MetaTrader 5 Administrator:

  * The connection status is shown by the gateway/data feed icon in the tree
  * The amount of transmitted traffic is displayed on the "Status" page of the selected gateway/data feed



![Data feed status](images/admin_datafeed_state.png)

The Gateway API provides the following functions to pass these parameters to the server and then to display the relevant information to the user:

Function | Purpose  
---|---  
[StateConnect](External-Connection-State/StateConnect.md) | Set the state of the gateway/data feed external connection.  
[StateTraffic](External-Connection-State/StateTraffic.md) | Add the value to the external connection traffic counter.  
  
Statistical data on the number of the passed ticks, Depth of Market changes and news is counted automatically.

```

---

<a id='main-interface-gateway-symbols-md'></a>
### 195. `Main-Interface/Gateway-Symbols.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Gateway Symbols

[Previous](Trade-Requests/RequestGetAll.md) | [Next](Gateway-Symbols/GatewaySymbolAdd.md)

# Gateway trading symbols

The functions described in this section pass to the MetaTrader 5 cluster the data about the parameters of trading symbols available to the gateway. This information (symbols) is passed only to the history server and is used only for internal purposes when [matching ECN orders through the gateway](https://support.metaquotes.net/en/docs/mt5/platform/administration/ecn/ecn_matching). Symbols created in this way are not available to clients.

ECN works with one set of symbols, to which data from different gateways are received. One set of settings is used for all symbols. For example, ECN has the EURUSD.ECN symbol, which receives data from three different gateways:

  * EURUSD.GW1
  * EURUSD.GW2
  * EURUSD.GW3



Each of these symbols has its own settings on the corresponding external system side, where these settings may differ. For example, the symbols may have different accuracy, contract size, etc. Several gateways cannot simultaneously import their settings into one symbol configuration on the trading platform side (using the [IMTGateway::Symbol*](Configuration-Databases/Symbols.md) methods).

To solve this situation, a separate option has been added to the Gateway API allowing the specification of symbol settings on the external system side. These settings are not imported to trade servers. They are only used in ECN to unify symbol settings from different systems.

[Translation settings](../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate.md) are applied to the list of symbols available to the gateway. For example, if the symbol name conversion EURUSD.GW1 -> EURUSD.ECN is specified in the gateway configuration, the settings of EURUSD.ECN will be transferred to the ECN.

> If the gateway does not pass the list of its symbols, the ECN will be able to receive Market Depth data and quotes from that gateway and collect them in an aggregated Market Depth, but will not be able to implement matching with the gateway orders. That is, all gateway levels in the Market Depth will be considered illiquid.

The following functions are provided for managing the gateway symbols:

The function | Purpose  
---|---  
[GatewaySymbolAdd](Gateway-Symbols/GatewaySymbolAdd.md) | Adds a new symbol to the list of symbols available to the gateway.  
[GatewaySymbolDelete](Gateway-Symbols/GatewaySymbolDelete.md) | Deletes a symbol from the list available to the gateway (by name).  
[GatewaySymbolClear](Gateway-Symbols/GatewaySymbolClear.md) | Clears the entire list of symbols available to the gateway.  
[GatewaySymbolTotal](Gateway-Symbols/GatewaySymbolTotal.md) | Gets the total number of symbols available to the gateway.  
[GatewaySymbolNext](Gateway-Symbols/GatewaySymbolNext.md) | Gets the description of a symbol available to the gateway, by index.  
[GatewaySymbolGet](Gateway-Symbols/GatewaySymbolGet.md) | Gets the description of a symbol available to the gateway, by name.

```

---

<a id='main-interface-history-data-md'></a>
### 195. `Main-Interface/History-Data.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / History Data

[Previous](Quote-and-News-Feeds/SendEconomicEvents.md) | [Next](History-Data/ChartRequest.md)

# History Data

The MetaTrader 5 Gateway API provides functions for working with historical price data of the platform that are available in the form of minute bars. They allow you to edit or delete minute bars.

Functions for working with historical data:

Function | Purpose  
---|---  
[ChartRequest](History-Data/ChartRequest.md) | Request minute bars for a symbol.  
[ChartDelete](History-Data/ChartDelete.md) | Delete a bar by the symbol.  
[ChartUpdate](History-Data/ChartUpdate.md) | Change historical data of a symbol.  
[ChartReplace](History-Data/ChartReplace.md) | Full replacement of history data in the specified period with the passed data.

```

---

<a id='main-interface-mail-database-md'></a>
### 195. `Main-Interface/Mail-Database.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Mail Database

[Previous](Synchronizing-Trading-Data/GatewayAccountSet.md) | [Next](Mail-Database/MailCreate.md)

# Mail Database

The functions described in this section allow to create and send mails via internal mail system.

Function | Purpose  
---|---  
[MailCreate](Mail-Database/MailCreate.md) | Create a message in the internal mail system.  
[MailSend](Mail-Database/MailSend.md) | Send emails via the internal mail system.

```

---

<a id='main-interface-processing-trade-requests-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Processing Trade Requests

[Previous](Gateway-Symbols/GatewaySymbolGet.md) | [Next](Processing-Trade-Requests/DealerConfirmCreate.md)

# Processing Trade Requests

In accordance with the ideology of the MetaTrader 5 trading platform, customer request management is carried out through a queue of trade requests. A gateway written with the help of the Gateway API acts as a dealer, who works with the queue, receiving the queue status, capturing and processing trade requests, and then reporting the results of their processing.

  * All the functions described in this section are used only for gateways.
  * Details of working with trade operations are described in the ["Trade Operations in Gateway API"](../Trade-Operations-in.md) section.

  
---  
  
The following dealer activity functions are available:

Functions | Purpose  
---|---  
[DealerConfirmCreate](Processing-Trade-Requests/DealerConfirmCreate.md) | Create request confirmation interface object.  
[DealerExecutionCreate](Processing-Trade-Requests/DealerExecutionCreate.md) | Create trade execution method of this object.  
[DealerStart](Processing-Trade-Requests/DealerStart.md) | Gateway connection to the trading platform as a dealer.  
[DealerStop](Processing-Trade-Requests/DealerStop.md) | DealerStart inverse method. After its successful execution the gateway will stop fulfilling the dealer functions.  
[DealerGetAsync](Processing-Trade-Requests/DealerGetAsync.md) | Capture the most early (old) request from the requests queue.  
[DealerLockAsync](Processing-Trade-Requests/DealerLockAsync.md) | Capture a request from the requests queue by ID.  
[DealerAnswerAsync](Processing-Trade-Requests/DealerAnswerAsync.md) | Return the results of the captured request processing.  
[DealerExecuteAsync](Processing-Trade-Requests/DealerExecuteAsync.md) | The platform notification on the order trade execution in the external system.

```

---

<a id='main-interface-quote-and-news-feeds-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Quote and News Feeds

[Previous](Client-Connection/ClientAllowIP.md) | [Next](Quote-and-News-Feeds/SendTickStats.md)

<a id="quote-and-news-streams"></a>
# Quote and News Streams (#quote-and-news-streams)

The functions described in this section allow sending quiting data and news to the platform. The following functions are provided:

Function | Purpose  
---|---  
[SendTickStats](Quote-and-News-Feeds/SendTickStats.md) | Sending statistical information about a financial instrument.  
[SendTicks](Quote-and-News-Feeds/SendTicks.md) | Sending current prices.  
[SendBookDiffs](Quote-and-News-Feeds/SendBookDiffs.md) | Sending the Depth of Market changes.  
[SendBooks](Quote-and-News-Feeds/SendBooks.md) | Sending the entire state of the Depth of Market.  
[SendNews](Quote-and-News-Feeds/SendNews.md) | Sending news.  
[SendEconomicEvents](Quote-and-News-Feeds/SendEconomicEvents.md) | Sending economic calendar events. The method is obsolete and is not supported.  
  
<a id="charts"></a>
## Chart Construction (#charts)

The trading platform (the history server) builds bars using ticks received from datafeeds and gateways. Depending on the [IMTConSymbol::ChartMode](../../Configuration-Interfaces/Symbols/IMTConSymbol/ChartMode.md) parameter, financial symbol bars are based on Bid or Last prices (the price of the last executed trade). As a rule, charts of exchange instruments with the enabled Market Depth feature are based on the Last price.

For the symbols, the charts of which are based on Bid prices, the history server does no accept Last prices and volumes from gateways and datafeeds. Such ticks are not saved and are not provided to other components of the platform. Therefore, when sending quotes using the [IMTGatewayAPI::SendTicks](Quote-and-News-Feeds/SendTicks.md) method, you should not fill the [MTTick::last](../../Structures/MTTick.md) and [MTTick::volume](../../Structures/MTTick.md) fields.

If a data feed or gateway sends symbol Market Depth changes to a platform ([IMTGatewayAPI::SendBookDiffs](Quote-and-News-Feeds/SendBookDiffs.md), [IMTGatewayAPI::SendBooks](Quote-and-News-Feeds/SendBooks.md)), the history server automatically monitors changes of the best Bid and Ask price in it. If the best Bid or Ask price has changed, the history server generates a tick with the values ​​of the best Bid and Ask prices. In this tick, the value of the last trade price and the volume will be zero. The gateway/datafeed must only send ticks with the filled Last price and volume value. The network traffic is saved, because Bid and Ask prices are not sent.

> For operations with the symbol's price history, use methods [IMTGatewayAPI::Chart*](History-Data.md) and [IMTGatewayAPI::TickHistory*](Tick-Data.md).

```

---

<a id='main-interface-server-md'></a>
### 195. `Main-Interface/Server.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Server

[Previous](Common-Functions/LicenseCheck.md) | [Next](Server/Start.md)

# Server

The functions described in this section allow to run and stop Gateway API server port for the platform connection and get the data on the current address and the port where Gateway API server port is launched.

The following functions are provided:

Function | Purpose  
---|---  
[Start](Server/Start.md) | Gateway API server port launch.  
[Stop](Server/Stop.md) | Gateway API server port stop.  
[ServerIP](Server/IP.md) | Get the IP address on which the Gateway API server port is running.  
[ServerPort](Server/Port.md) | Get the number of the port used for the connection to Gateway API.  
[ServerConnections](Server/Connections.md) | Get the number of the current connections to the Gateway API server port.

```

---

<a id='main-interface-synchronizing-trading-data-md'></a>
### 195. `Main-Interface/Synchronizing-Trading-Data.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Synchronizing Trading Data

[Previous](Controlling-Orders-in-External-System/GatewayOrdersAnswer.md) | [Next](Synchronizing-Trading-Data/GatewayAccountAnswer.md)

# Synchronizing Trading Data

MetaTrader 5 Gateway API provides possibility to synchronize MetaTrader 5 client trading data with an external trading system.

## Synchronizing on Request from MetaTrader 5

If the gateway has such a functionality, the platform administrator can synchronize this data on the account management page via MetaTrader 5 Administrator:

![Synchronizing with an external system](images/gateway_synchronize.png)

When clicking "Synchronize" in MetaTrader 5 Administrator or when calling IMTAdminAPI::UserExternalSync and IMTManagerAPI::UserExternalSync methods from MetaTrader 5 Manager API, [IMTGatewaySink::HookGatewayAccountRequest](../Event-Interface/HookGatewayAccountRequest.md) hook is called. Pending orders, positions and client balances are synchronized with an external system using the hook and [GatewayAccountAnswer](Synchronizing-Trading-Data/GatewayAccountAnswer.md) function.

## Synchronizing on Request from an External System

There is also the possibility to change the client data on MetaTrader 5 side without requesting the platform administrator. The complete structure looks as follows:

  * The gateway receives information that the data of some users in an external system has changed. These users have certain account number in that external system.
  * In order to define the users present in MetaTrader 5, [IMTGaewayAPI::User*](Users.md) methods should be used. They allow you to receive the list of the users available to the gateway on MetaTrader 5 side, as well as the account numbers in the external trading system specified for these users.
  * After receiving the list of users, it is possible to request their status on MetaTrader 5 side. This will allow you to define if their status should be synchronized with MetaTrader 5. Request for users' status is performed using [IMTGatewayAPI::GatewayAccountRequest](Synchronizing-Trading-Data/GatewayAccountRequest.md) method. The data requested using such method is passed to [IMTGatewaySink::OnGatewayAccountAnswer](../Event-Interface/OnGatewayAccountAnswer.md) handler.
  * [IMTGatewayAPI::GatewayAccountSet](Synchronizing-Trading-Data/GatewayAccountSet.md) method should be used to synchronize the status of the external trading system's users with MetaTrader 5. Execution result, as well as the final status of client entries after the synchronization are passed to [IMTGatewaySink::OnGatewayAccountSet](../Event-Interface/OnGatewayAccountSet.md) handler.



```

---

<a id='main-interface-tick-data-md'></a>
### 195. `Main-Interface/Tick-Data.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Tick Data

[Previous](History-Data/ChartReplace.md) | [Next](Tick-Data/TickHistoryRequest.md)

# Tick Data Functions

The MetaTrader 5 Gateway API features functions for the export and import of tick data to the platform. Unlike [SendTicks*](Quote-and-News-Feeds/SendTicks.md), these functions work directly with the history of ticks, rather than the price stream which is broadcast to clients in real time.

Function | Purpose  
---|---  
[TickHistoryRequest](Tick-Data/TickHistoryRequest.md) | Get quotes for a symbol in the specified time range.  
[TickHistoryRequestRaw](Tick-Data/TickHistoryRequestRaw.md) | Get the entire stream of quotes for a symbol (raw and processed prices in accordance with the configuration of the symbol) in the specified time range.  
[TickHistoryAdd](Tick-Data/TickHistoryAdd.md) | Add tick data of a symbol.  
[TickHistoryReplace](Tick-Data/TickHistoryReplace.md) | Completely replace tick data in the specified period by the transmitted data

```

---

<a id='main-interface-trade-databases-md'></a>
### 195. `Main-Interface/Trade-Databases.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Trade Databases

[Previous](Configuration-Databases/Spreads/SpreadGet.md) | [Next](Trade-Databases/OrderCreate.md)

# Trade Databases

Functions described in this section allow working with the trading databases of the MetaTrader 5 platform.

Function | Purpose  
---|---  
[OrderCreate](Trade-Databases/OrderCreate.md) | Create an object of a trade order.  
[PositionCreate](Trade-Databases/PositionCreate.md) | Create an object of a trade position.

```

---

<a id='main-interface-trade-requests-md'></a>
### 195. `Main-Interface/Trade-Requests.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Trade Requests

[Previous](Trade-Databases/PositionCreate.md) | [Next](Trade-Requests/RequestCreate.md)

# Trade Requests

Functions described in this section allow working with the server trade requests queue. They allow to get existing trade requests and subscribe to events associated with changes in the queue of requests.

The following functions are available for working with trade requests:

Function | Purpose  
---|---  
[RequestCreate](Trade-Requests/RequestCreate.md) | Create an object of a trade request.  
[RequestArrayCreate](Trade-Requests/RequestArrayCreate.md) | Create an object of the array of trade requests.  
[RequestSubscribe](Trade-Requests/RequestSubscribe.md) | Subscribe to events associated with trade requests queue changes.  
[RequestUnsubscribe](Trade-Requests/RequestUnsubscribe.md) | Unsubscribe from events associated with requests queue changes.  
[RequestTotal](Trade-Requests/RequestTotal.md) | Get the total amount of trade requests in a requests queue.  
[RequestNext](Trade-Requests/RequestNext.md) | Get a trade request by a queue position.  
[RequestGet](Trade-Requests/RequestGet.md) | Get a trade request by ID.  
[RequestGetAll](Trade-Requests/RequestGetAll.md) | Get all the trade requests in a queue.

```

---

<a id='main-interface-user-settings-md'></a>
### 195. `Main-Interface/User-Settings.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / User Settings

[Previous](Mail-Database/MailSend.md) | [Next](User-Settings/SettingsAdd.md)

# Custom Settings

The functions described in this section allow managing additional custom settings of gateways and data feeds. These settings are saved in the file settings.dat, which is created in the [working directory](../Exported-Functions/MTGatewayCreateLocal.md) of the application. The working directory is in the same directory where the executable file of the gateway or data feed is located.

> Custom settings are not associated with [configurations of gateways](../../Configuration-Interfaces/Gateways.md) and [data feeds](../../Configuration-Interfaces/Data-Feeds.md). They allow storing data in a local file.

The following functions are available for working with custom settings:

Function | Purpose  
---|---  
[SettingsAdd](User-Settings/SettingsAdd.md) | Add a setting.  
[SettingsUpdate](User-Settings/SettingsUpdate.md) | Change a setting by its position and name.  
[SettingsDelete](User-Settings/SettingsDelete.md) | Delete a setting by its position and name.  
[SettingsClear](User-Settings/SettingsClear.md) | Delete all settings.  
[SettingsTotal](User-Settings/SettingsTotal.md) | Get the number of settings.  
[SettingsNext](User-Settings/SettingsNext.md) | Get a setting by its position.  
[SettingsGet](User-Settings/SettingsGet.md) | Get a setting by its name.

```

---

<a id='main-interface-users-md'></a>
### 195. `Main-Interface/Users.md`

```markdown
[🏠 Document Start](../../README.md) / [Gateway API](../README.md) / [Main Interface](../Main-Interface.md) / Users

[Previous](Tick-Data/TickHistoryReplace.md) | [Next](Users/UserCreate.md)

# Users

Functions of Gateway API allow accessing the user database on the trade server as well as subscribing and unsubscribing from events connected with changes in this database.

Functions | Purpose  
---|---  
[UserCreate](Users/UserCreate.md) | Create an object of a client record.  
[UserCreateAccount](Users/UserCreate.md) | Create an object of a client's trading account.  
[UserSubscribe](Users/UserSubscribe.md) | Subscribe to events associated with changes in the client base.  
[UserUnsubscribe](Users/UserUnsubscribe.md) | Unsubscribe from events associated with changes in the client base.  
[UserTotal](Users/UserTotal.md) | Get the total number of users in groups available to the gateway.  
[UserGet](Users/UserGet.md) | Get a client record by the login.  
[UserGetByAccount](Users/UserGetByAccount.md) | Get a client record, which corresponds to the account number in the external trading system.  
[UserGroup](Users/UserGroup.md) | Get the group of a client by the login.  
[UserLogins](Users/UserLogins.md) | Returns an array of logins of the clients who are included in the specified group.

```

---

<a id='main-interface-client-connection-clientadd-md'></a>
### 195. `Main-Interface/Client-Connection/ClientAdd.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Client Connection](../Client-Connection.md) / ClientAdd

[Previous](../Client-Connection.md) | [Next](ClientAllowIP.md)

# IMTGatewayAPI::ClientAdd

Adding permission for the platform components connection using a specified login and a password.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ClientAdd(
       const UINT64  login,        // Login
       LPCWSTR       password      // Password
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.ClientAdd(
       ulong         login,        // Login
       string        password      // Password
       )

### Parameters

**login**  
[in] Login to connect the platform components to a remote gateway/data feed.

**password**  
[in] Paasword to connect the platform components to a remote gateway/data feed.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

This method is used only for the remote gateways and data feeds. By default, connection with any logins and passwords is forbidden.

```

---

<a id='main-interface-client-connection-clientallowip-md'></a>
### 195. `Main-Interface/Client-Connection/ClientAllowIP.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Client Connection](../Client-Connection.md) / ClientAllowIP

[Previous](ClientAdd.md) | [Next](../Quote-and-News-Feeds.md)

# IMTGatewayAPI::ClientAllowIP

Adding permission for the connection from a specified IP address.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ClientAllowIP(
       LPCWSTR  address      // IP address
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.ClientAllowIP(
       string   address      // IP address
       )

### Parameters

**address**  
[in] IP address, from which connection must be allowed.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

By default, connection from any IP addresses is allowed. In case at least one address is added, connections from all addresses, except from the added ones, are forbidden.

```

---

<a id='main-interface-common-functions-allocate-md'></a>
### 195. `Main-Interface/Common-Functions/Allocate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / Allocate

[Previous](../Common-Functions.md) | [Next](Free.md)

# IMTGatewayAPI::Allocate

Memory allocation by an application. It is paired to the [IMTGatewayAPI::Free](Free.md) method.
    
    
    void*  IMTGatewayAPI::Allocate(
       const UINT  bytes      // Amount of allocated memory
       )

### Parameters

**bytes**  
[in] Amount of allocated memory in bytes.

### Return Value

If successful, it returns a pointer to the allocated memory block, otherwise it returns NULL.

```

---

<a id='main-interface-common-functions-free-md'></a>
### 195. `Main-Interface/Common-Functions/Free.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / Free

[Previous](Allocate.md) | [Next](LoggerOut.md)

# IMTGatewayAPI::Free

Free memory allocated earlier by [IMTGatewayAPI::Allocate](Allocate.md). It is used to free memory allocated by the functions and interfaces of the MetaTrader 5 Gateway API.
    
    
    void  IMTGatewayAPI::Free(
       void*  ptr      // Pointer to a memory block
       )

### Parameters

**ptr**  
[in] A pointer to the released memory block allocated earlier byIMTGatewayAPI::Allocate.

```

---

<a id='main-interface-common-functions-licensecheck-md'></a>
### 195. `Main-Interface/Common-Functions/LicenseCheck.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / LicenseCheck

[Previous](Release.md) | [Next](../Server.md)

# IMTGatewayAPI::LicenseCheck

Check the gateway/data feed usage license.

C++
    
    
    MTAPIRES  IMTGatewayAPI::LicenseCheck(
       MTLicenseCheck&     check   // Structure for verifying the license
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.LicenseCheck(
       ref MTLicenseCheck  check   // Structure for verifying the license
       )

### Parameters

**check**  
[in] The reference to theMTLicenseCheckstructure intended for gateway/data feed usage module license verification.

### Return Value

An indication of a successful verification is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

The method can only be called after receiving the [IMTGatewaySink::OnGatewayStart](../../Event-Interface/OnGatewayStart.md) notification.

## Working with licenses

MetaTrader 5 Gateway API allows to protect developments from unauthorized use. Protection is developed to allow to verify gateway/data feed usage authorization in the MetaTrader 5 platform license generated by the platform developer company [MetaQuotes Ltd.](https://www.metaquotes.net/ "MetaQuotes Software Corp. ")

The algorithm for working with the license is described below:

• Gateway/data feed unique name is specified in the program code.

• The module name must be sent to MetaQuotes Software Corp. to include it to the MetaTrader 5 platform licenses of the indicated companies.

• The IMTGatewayAPI::LicenseCheck method is called, in which the filled [MTLicenseCheck](../../../Structures/MTLicenseCheck.md) structure is transferred as a parameter. The following fields must be filled in the structure:
* The IMTGatewayAPI::LicenseCheck method sends specified data to a server.
* The server checks whether the use of the module with a specified name is allowed.
* The server sends the MTLicenseCheck structure back with additionally filled fields:
* The module signs the same data (retcode+name+random) by its public key and compares result with the sign received from the server. This is how received data identity verification is performed.

• name — a name of a previously determined module;

• random — a random sequence up to 256 symbols long;

• random_size — generated sequence size.

> Special [CMTGatewayAPIFactory::LicenseCheck](../../CMTGatewayAPIFactory/LicenseCheck.md) method is provided in the Gateway API factory to ease the license verification. Main part of the license verification actions specified above are implemented in this method. While using the factory method, a programmer has only to transmit to it a pointer to the Gateway API and gateway/data feed module name.

### Example
    
    
    //+------------------------------------------------------------------+
    //| Request Queue Processing                                         |
    //+------------------------------------------------------------------+
    void CMTGatewayApp::OnDealerLock(const MTAPIRES retcode,const IMTRequest *request,
                                     const IMTUser *user,const IMTAccount *account,
                                     const IMTOrder *order,const IMTPosition *position)
      {
    //---
       if(m_gateway)
         {
          //--- Checking the license when the first request is received
          if(m_requests_count=0)
            {
             //--- checking
             if((m_license_retcode=m_api_factory.LicenseCheck(m_gateway,L"FXBR5GWTTEST"))!=MT_RET_OK)
                ExtLogger.Out(MTLogAtt,L"No licence, running in demo mode [%i]",m_license_retcode);
             //--- Forward request for further processing and increase the request counter
             m_gateway->OnGatewayDealerLock(retcode,request);
             i++;
            }
          else
            {
             //--- Previous check result will be used for all further requests
             if(m_requests_count<=100)
               {
                m_gateway->OnGatewayDealerLock(retcode,request);
                i++;
               }
             //--- Without a license, use the demo mode, process only the first 100 requests
             if(m_license_retcode!=MT_RET_OK && m_requests_count>100)
               {
                ExtLogger.Out(MTLogAtt,L"Trial version is limited to 100 requests [%i]",m_license_retcode);
                retcode=MT_RET_ERROR;
                //--- Pass the request and an error to stop finish request processing
                m_gateway->OnGatewayDealerLock(retcode,request);
               }
            }
         }
      }
    //+------------------------------------------------------------------+

```

---

<a id='main-interface-common-functions-loggerflush-md'></a>
### 195. `Main-Interface/Common-Functions/LoggerFlush.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / LoggerFlush

[Previous](LoggerOutString.md) | [Next](Release.md)

# IMTGatewayAPI::LoggerFlush

Flush the file buffer of the journal to a disk.

C++
    
    
    void  IMTGatewayAPI::LoggerFlush()

.NET
    
    
    void  CIMTGatewayAPI.LoggerFlush()

```

---

<a id='main-interface-common-functions-loggerout-md'></a>
### 195. `Main-Interface/Common-Functions/LoggerOut.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / LoggerOut

[Previous](Free.md) | [Next](LoggerOutString.md)

# IMTGatewayAPI::LoggerOut

Log messages.

C++
    
    
    MTAPIRES  IMTGatewayAPI::LoggerOut(
       const UINT        code,   // Message code
       LPCWSTR           msg,    // Message string
                         ...     // Optional arguments
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.LoggerOut(
       EnMTLogCode      code,    // Message code
       string           format,  // Message string
       params object[]  args     // Optional arguments
       )

### Parameters

**code**  
[in] Message code that is passed using theEnMTLogCodeenumeration.

**msg**  
[in] A message string with optional arguments.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Each string is limited to 16KB without the standard string header.

```

---

<a id='main-interface-common-functions-loggeroutstring-md'></a>
### 195. `Main-Interface/Common-Functions/LoggerOutString.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / LoggerOutString

[Previous](LoggerOut.md) | [Next](LoggerFlush.md)

# IMTGatewayAPI::LoggerOutString

Quick output of unformatted stings to the journal.

C++
    
    
    MTAPIRES  IMTGatewayAPI::LoggerOutString(
       const UINT        code,   // log code
       LPCWSTR           string  // log string
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.LoggerOutString(
       EnMTLogCode      code,    // log code
       string           string   // log string
       )

### Parameters

**code**  
[in] Log code which is passed using theEnMTLogCodeenumerations.

**msg**  
[in] The message string.

### Return Value

An indication of a successful execution is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

Compared to [IMTGatewayAPI::LoggerOut](LoggerOut.md), which formats the output, this method consumes less resources.

```

---

<a id='main-interface-common-functions-release-md'></a>
### 195. `Main-Interface/Common-Functions/Release.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Common Functions](../Common-Functions.md) / Release

[Previous](LoggerFlush.md) | [Next](LicenseCheck.md)

# IMTGatewayAPI::Release

A standard method of object removing. After the method call, the object cannot be accessed, because it has been deleted.

C++
    
    
    void  IMTGatewayAPI::Release()

.NET
    
    
    void  CIMTGatewayAPI.Release()

```

---

<a id='main-interface-configuration-databases-common-md'></a>
### 195. `Main-Interface/Configuration-Databases/Common.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Common

[Previous](../Configuration-Databases.md) | [Next](Common/Create.md)

# Common Configuration

By using the functions described in this section, you can receive the system-wide platform configuration, as well as subscribe and unsubscribe from events associated with configuration changes.

Function | Purpose  
---|---  
[CommonCreate](Common/Create.md) | Create a common platform configuration object.  
[CommonSubscribe](Common/Subscribe.md) | Subscribe to events associated with the common configuration of the platform.  
[CommonUnsubscribe](Common/Unsubscribe.md) | Unsubscribe from events associated with the common configuration of the platform.  
[CommonGet](Common/Get.md) | Get the common platform configuration.

```

---

<a id='main-interface-configuration-databases-data-feeds-md'></a>
### 195. `Main-Interface/Configuration-Databases/Data-Feeds.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Data Feeds

[Previous](Common/Get.md) | [Next](Data-Feeds/FeederCreate.md)

# Data Feed Configuration

The functions described in this section allow to get data feeds configurations:

Function | Purpose  
---|---  
[FeederCreate](Data-Feeds/FeederCreate.md) | Create an object of the data feed configuration.  
[FeederParamCreate](Data-Feeds/FeederParamCreate.md) | Create an object of the parameter of the data feeds.  
[FeederTranslateCreate](Data-Feeds/FeederTranslateCreate.md) | Create an object of setup of converting the information transmitted from a data feed.

```

---

<a id='main-interface-configuration-databases-gateways-md'></a>
### 195. `Main-Interface/Configuration-Databases/Gateways.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Gateways

[Previous](Data-Feeds/FeederTranslateCreate.md) | [Next](Gateways/GatewayCreate.md)

# Gateway Configuration

The functions described in this section allow to get gateways configurations.

Function | Purpose  
---|---  
[GatewayCreate](Gateways/GatewayCreate.md) | Create an object of the gateway configuration.  
[GatewayParamCreate](Gateways/GatewayParamCreate.md) | Create an object of the gateway parameter.  
[GatewayTranslateCreate](Gateways/GatewayTranslateCreate.md) | Create an object of the parameter for converting the information received by the gateway.

```

---

<a id='main-interface-configuration-databases-groups-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Groups

[Previous](Symbols/SymbolGet.md) | [Next](Groups/GroupCreate.md)

# Configuration of Groups

The functions allow to get groups configuration, as well as subscribe and unsubscribe from events associated with their change.

The following functions for managing groups are available:

Function | Purpose  
---|---  
[GroupCreate](Groups/GroupCreate.md) | Create an object of the group configuration.  
[GroupSymbolCreate](Groups/GroupSymbolCreate.md) | Create an object of symbol configuration for a group.  
[GroupCommissionCreate](Groups/GroupCommissionCreate.md) | Create an object of commission configuration for a group.  
[GroupTierCreate](Groups/GroupTierCreate.md) | Create an object of commission range configuration for a group.  
[GroupSubscribe](Groups/GroupSubscribe.md) | Subscribe to events and hooks associated with the groups configuration.  
[GroupUnsubscribe](Groups/GroupUnsubscribe.md) | Unsubscribe from events and hooks associated with the groups configuration.  
[GroupTotal](Groups/GroupTotal.md) | Get the number of the groups configurations available for a gateway.  
[GroupNext](Groups/GroupNext.md) | Get the group configuration by the index.  
[GroupGet](Groups/GroupGet.md) | Get the group configuration by the name.

```

---

<a id='main-interface-configuration-databases-network-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Network

[Previous](Time/Get.md) | [Next](Network/NetServerCreate.md)

# Network Configuration

Functions allow managing the configuration of the platform components, as well subscribe and unsubscribe from events associated with its change.

To manage the configuration of components, the following functions are available:

Function | Purpose  
---|---  
[NetServerCreate](Network/NetServerCreate.md) | Create an object of the network configuration.  
[NetServerRangeCreate](Network/NetServerRangeCreate.md) | Create an object of the range of orders, deals or accounts.  
[NetServerSubscribe](Network/NetServerSubscribe.md) | Subscribe to events associated with the network configuration.  
[NetServerUnsubscribe](Network/NetServerUnsubscribe.md) | Unsubscribe from events associated with the network configuration.  
[NetServerTotal](Network/NetServerTotal.md) | The total number of server configurations available in the platform.  
[NetServerNext](Network/NetServerNext.md) | Get a server configuration by the index.  
[NetServerGet](Network/NetServerGet.md) | Get a server configuration by the ID.

```

---

<a id='main-interface-configuration-databases-spreads-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Spreads

[Previous](Network/NetServerGet.md) | [Next](Spreads/SpreadCreate.md)

# Configuration of Spreads

Functions allow managing spreads, as well subscribe and unsubscribe from events associated with their change.

The following functions for managing spreads are available:

Function | Purpose  
---|---  
[SpreadCreate](Spreads/SpreadCreate.md) | Create an object of the configuration of a spread.  
[SpreadLegCreate](Spreads/SpreadLegCreate.md) | Create an object of the configuration of a spread leg.  
[SpreadSubscribe](Spreads/SpreadSubscribe.md) | Subscribe to events and hooks associated with the configuration of spreads.  
[SpreadUnsubscribe](Spreads/SpreadUnsubscribe.md) | Unsubscribe from events and hooks associated with spread configuration.  
[SpreadAdd](Spreads/SpreadAdd.md) | Add or update a spread configuration.  
[SpreadDelete](Spreads/SpreadDelete.md) | Deleting a spread configuration by the index.  
[SpreadShift](Spreads/SpreadShift.md) | Change the position of a spread configuration in the list.  
[SpreadTotal](Spreads/SpreadTotal.md) | The total number of spread configurations available in the platform.  
[SpreadNext](Spreads/SpreadNext.md) | Receiving a spread configuration by the index.  
[SpreadGet](Spreads/SpreadGet.md) | Receiving a spread configuration by the identifier.

```

---

<a id='main-interface-configuration-databases-symbols-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Symbols

[Previous](Gateways/GatewayTranslateCreate.md) | [Next](Symbols/SymbolCreate.md)

# Configuration of Symbols

The functions described in this section allow to manage symbols, as well as subscribe and unsubscribe from events associated with their change.

The following functions for managing symbols are available:

Function | Purpose  
---|---  
[SymbolCreate](Symbols/SymbolCreate.md) | Create an object of the symbol configuration.  
[SymbolSessionCreate](Symbols/SymbolSessionCreate.md) | Create an object of configuration of a trading or quoting session of the symbol.  
[SymbolSubscribe](Symbols/SymbolSubscribe.md) | Subscribe to events and hooks associated with the configuration of symbols.  
[SymbolUnsubscribe](Symbols/SymbolUnsubscribe.md) | Unsubscribe from events and hooks associated with the configuration of symbols.  
[SymbolAddPreliminary](Symbols/SymbolAddPreliminary.md) | Add or update a preliminary configuration of a symbol.  
[SymbolUpdate](Symbols/SymbolUpdate.md) | Add or update a symbol configuration.  
[SymbolDelete](Symbols/SymbolDelete.md) | Delete a symbol configuration by the index or name.  
[SymbolTotal](Symbols/SymbolTotal.md) | Get the number of the symbols configurations avaialble for a gateway or a data feed.  
[SymbolNext](Symbols/SymbolNext.md) | Get the symbol configuration by the index.  
[SymbolGet](Symbols/SymbolGet.md) | Get a symbol configuration or an individual configuration of a symbol for a group by the name of the symbol.

```

---

<a id='main-interface-configuration-databases-time-md'></a>
### 195. `Main-Interface/Configuration-Databases/Time.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Configuration Databases](../Configuration-Databases.md) / Time

[Previous](Groups/GroupGet.md) | [Next](Time/Create.md)

# Time Configuration

Functions allow getting the time configurations of the platform, as well as subscribe and unsubscribe from events associated with its change.

The following functions are available for working with the time configurations:

Function | Purpose  
---|---  
[TimeCreate](Time/Create.md) | Create an object of the time configuration.  
[TimeSubscribe](Time/Subscribe.md) | Subscribe to events and hooks associated with the time configuration.  
[TimeUnsubscribe](Time/Unsubscribe.md) | Unsubscribe from events and hooks associated with the time configuration.  
[TimeCurrent](Time/Current.md) | Get the current time configuration.  
[TimeGet](Time/Get.md) | Get the time configuration.

```

---

<a id='main-interface-configuration-databases-common-create-md'></a>
### 195. `Main-Interface/Configuration-Databases/Common/Create.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Common](../Common.md) / Create

[Previous](../Common.md) | [Next](Subscribe.md)

# IMTGatewayAPI::CommonCreate

Create a common platform configuration object.

C++
    
    
    IMTConCommon*  IMTGatewayAPI::CommonCreate()

.NET
    
    
    CIMTConCommon  CIMTGatewayAPI.CommonCreate()

### Return Value

Returns a pointer to the created object that implements the [IMTConCommon](../../../../Configuration-Interfaces/Common/IMTCon.md) interface. Null is returned in case of failure.

### Note

The created object must be destroyed by calling the [IMTConCommon::Release](../../../../Configuration-Interfaces/Common/IMTConCommon/IMTCon-Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-common-get-md'></a>
### 195. `Main-Interface/Configuration-Databases/Common/Get.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Common](../Common.md) / Get

[Previous](Unsubscribe.md) | [Next](../Data-Feeds.md)

# IMTGatewayAPI::CommonGet

Get the common platform configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::CommonGet(
       IMTConCommon*  common      // Configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.CommonGet(
       CIMTConCommon  common      // Configuration
       )

### Parameters

**common**  
[out] A common configuration object. The object must first be created using theIMTGatewayAPI::CommonCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method is not available for data feeds.

```

---

<a id='main-interface-configuration-databases-common-subscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Common/Subscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Common](../Common.md) / Subscribe

[Previous](Create.md) | [Next](Unsubscribe.md)

# IMTGatewayAPI::CommonSubscribe

Subscribe to events associated with the common configuration of the platform.

C++
    
    
    MTAPIRES  IMTGatewayAPI::CommonSubscribe(
       IMTConCommonSink*  sink      // Pointer to the IMTConCommonSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.CommonSubscribe(
       CIMTConCommonSink  sink      // CIMTConCommonSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConCommonSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same [IMTConCommonSink](../../../../Configuration-Interfaces/Common/IMTConSink.md) interface cannot subscribe to an event twice. The [MT_RET_ERR_DUPLICATE](../../../../Return-Codes/Common-errors.md) response code is returned in this case.

```

---

<a id='main-interface-configuration-databases-common-unsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Common/Unsubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Common](../Common.md) / Unsubscribe

[Previous](Subscribe.md) | [Next](Get.md)

# IMTGatewayAPI::CommonUnsubscribe

Unsubscribe from events associated with the common configuration of the platform.

C++
    
    
    MTAPIRES  IMTGatewayAPI::CommonUnsubscribe(
       IMTConCommonSink*  sink      // Pointer to the IMTConCommonSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.CommonUnsubscribe(
       CIMTConCommonSink  sink      // CIMTConCommonSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConCommonSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This is a pair method to [IMTGatewayAPI::CommonSubscribe](Subscribe.md). If an attempt is made to unsubscribe from the interface which has not been previously subscribed, the [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) error is returned.

The method is not available for data feeds.

```

---

<a id='main-interface-configuration-databases-data-feeds-feedercreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Data-Feeds/FeederCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Data Feeds](../Data-Feeds.md) / FeederCreate

[Previous](../Data-Feeds.md) | [Next](FeederParamCreate.md)

# IMTGatewayAPI::FeederCreate

Create an object of the data feed configuration.

C++
    
    
    IMTConFeeder*  IMTGatewayAPI::FeederCreate()

.NET
    
    
    CIMTConFeeder  CIMTGatewayAPI.FeederCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConFeeder](../../../../Configuration-Interfaces/Data-Feeds/IMTConFeeder.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConFeeder::Release](../../../../Configuration-Interfaces/Data-Feeds/IMTConFeeder/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-data-feeds-feederparamcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Data-Feeds/FeederParamCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Data Feeds](../Data-Feeds.md) / FeederParamCreate

[Previous](FeederCreate.md) | [Next](FeederTranslateCreate.md)

# IMTGatewayAPI::FeederParamCreate

Create an object of the parameter of the data feeds.

C++
    
    
    IMTConParam*  IMTGatewayAPI::FeederParamCreate()

.NET
    
    
    CIMTConParam  CIMTGatewayAPI.FeederParamCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConParam](../../../../Configuration-Interfaces/Additional-Parameters/IMTConParam.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConParam::Release](../../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-data-feeds-feedertranslatecreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Data-Feeds/FeederTranslateCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Data Feeds](../Data-Feeds.md) / FeederTranslateCreate

[Previous](FeederParamCreate.md) | [Next](../Gateways.md)

# IMTGatewayAPI::FeederTranslateCreate

Create an object of setup of converting the information transmitted from a data feed.

C++
    
    
    IMTConFeederTranslate*  IMTGatewayAPI::FeederTranslateCreate()

.NET
    
    
    CIMTConFeederTranslate  CIMTGatewayAPI.FeederTranslateCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConFeederTranslate](../../../../Configuration-Interfaces/Data-Feeds/IMTConFeederTranslate.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConFeederTranslate::Release](../../../../Configuration-Interfaces/Data-Feeds/IMTConFeederTranslate/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-gateways-gatewaycreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Gateways/GatewayCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Gateways](../Gateways.md) / GatewayCreate

[Previous](../Gateways.md) | [Next](GatewayParamCreate.md)

# IMTGatewayAPI::GatewayCreate

Create an object of the gateway configuration.

C++
    
    
    IMTConGateway*  IMTGatewayAPI::GatewayCreate()

.NET
    
    
    CIMTConGateway  CIMTGatewayAPI.GatewayCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConGateway](../../../../Configuration-Interfaces/Gateways/IMTConGateway.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConGateway::Release](../../../../Configuration-Interfaces/Gateways/IMTConGateway/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-gateways-gatewayparamcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Gateways/GatewayParamCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Gateways](../Gateways.md) / GatewayParamCreate

[Previous](GatewayCreate.md) | [Next](GatewayTranslateCreate.md)

# IMTGatewayAPI::GatewayParamCreate

Create an object of the gateway parameter.

C++
    
    
    IMTConParam*  IMTGatewayAPI::GatewayParamCreate()

.NET
    
    
    CIMTConParam  CIMTGatewayAPI.GatewayParamCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConParam](../../../../Configuration-Interfaces/Additional-Parameters/IMTConParam.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConParam::Release](../../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-gateways-gatewaytranslatecreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Gateways/GatewayTranslateCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Gateways](../Gateways.md) / GatewayTranslateCreate

[Previous](GatewayParamCreate.md) | [Next](../Symbols.md)

# IMTGatewayAPI::GatewayTranslateCreate

Create an object of the parameter for converting the information received by the gateway.

C++
    
    
    IMTConGatewayTranslate*  IMTGatewayAPI::GatewayTranslateCreate()

.NET
    
    
    CIMTConGatewayTranslate  CIMTGatewayAPI.GatewayTranslateCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConGatewayTranslate](../../../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConGatewayTranslate::Release](../../../../Configuration-Interfaces/Gateways/IMTConGatewayTranslate/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-groups-groupcommissioncreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupCommissionCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupCommissionCreate

[Previous](GroupSymbolCreate.md) | [Next](GroupTierCreate.md)

# IMTGatewayAPI::GroupCommissionCreate

Create an object of commission configuration for a group.

C++
    
    
    IMTConCommission*  IMTGatewayAPI::GroupCommissionCreate()

.NET
    
    
    CIMTConCommission  CIMTGatewayAPI.GroupCommissionCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConCommission](../../../../Configuration-Interfaces/Groups/IMTConCommission.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConCommission::Release](../../../../Configuration-Interfaces/Groups/IMTConCommission/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-groups-groupcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupCreate

[Previous](../Groups.md) | [Next](GroupSymbolCreate.md)

# IMTGatewayAPI::GroupCreate

Create an object of the group configuration.

C++
    
    
    IMTConGroup*  IMTGatewayAPI::GroupCreate()

.NET
    
    
    CIMTConGroup  CIMTGatewayAPI.GroupCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConGroup](../../../../Configuration-Interfaces/Groups/IMTConGroup.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConGroup::Release](../../../../Configuration-Interfaces/Groups/IMTConGroup/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-groups-groupget-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupGet.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupGet

[Previous](GroupNext.md) | [Next](../Time.md)

# IMTGatewayAPI::GroupGet

Get the group configuration by the name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GroupGet(
       LPCWSTR       name,      // Name of the configuration
       IMTConGroup*  group      // Group configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GroupGet(
       string        name,      // Name of the configuration
       CIMTConGroup  group      // Group configuration object
       )

### Parameters

**name**  
[in] The name of the configuration.

**group**  
[out] An object of group configuration. The group object must be first created using theIMTGatewayAPI::GroupCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The [IMTConGroup::Group()](../../../../Configuration-Interfaces/Groups/IMTConGroup/Group.md) value is used as the name.

```

---

<a id='main-interface-configuration-databases-groups-groupnext-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupNext.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupNext

[Previous](GroupTotal.md) | [Next](GroupGet.md)

# IMTGatewayAPI::GroupNext

Get the group configuration by the index.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GroupNext(
       const UINT    pos,       // Position of the configuration
       IMTConGroup*  group      // Group configuration object
       )

.NET
    
    
    MTRetcCode  CIMTGatewayAPI.GroupNext(
       uint          pos,       // Position of the configuration
       CIMTConGroup  group      // Group configuration object
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

**group**  
[out] An object of group configuration. The group object must be first created using theIMTGatewayAPI::GroupCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This method copies the configuration data of a group with a specified index to the group object.

```

---

<a id='main-interface-configuration-databases-groups-groupsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupSubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupSubscribe

[Previous](GroupTierCreate.md) | [Next](GroupUnsubscribe.md)

# IMTGatewayAPI::GroupSubscribe

Subscribe to events and hooks associated with the groups configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GroupSubscribe(
       IMTConGroupSink*  sink      // A pointer to the IMTConGroupSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GroupSubscribe(
       CIMTConGroupSink  sink      // CIMTConGroupSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConGroupSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same interface [IMTConGroupSink](../../../../Configuration-Interfaces/Groups/IMTConGroupSink.md) cannot subscribe to an event twice - in this case the response code [MT_RET_ERR_DUPLICATE](../../../../Return-Codes/Common-errors.md) is returned.

```

---

<a id='main-interface-configuration-databases-groups-groupsymbolcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupSymbolCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupSymbolCreate

[Previous](GroupCreate.md) | [Next](GroupCommissionCreate.md)

# IMTGatewayAPI::GroupSymbolCreate

Create an object of [symbol](../../../../Configuration-Interfaces/Symbols.md) configuration for a group.

C++
    
    
    IMTConGroupSymbol*  IMTGatewayAPI::GroupSymbolCreate()

.NET
    
    
    CIMTConGroupSymbol  CIMTGatewayAPI.GroupSymbolCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConGroupSymbol](../../../../Configuration-Interfaces/Groups/IMTConGroupSymbol.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConGroupSymbol::Release](../../../../Configuration-Interfaces/Groups/IMTConGroupSymbol/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-groups-grouptiercreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupTierCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupTierCreate

[Previous](GroupCommissionCreate.md) | [Next](GroupSubscribe.md)

# IMTGatewayAPI::GroupTierCreate

Create an object of commission range configuration for a group.

C++
    
    
    IMTConCommTier*  IMTGatewayAPI::GroupTierCreate()

.NET
    
    
    CIMTConCommTier  CIMTGatewayAPI.GroupTierCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConCommTier](../../../../Configuration-Interfaces/Groups/IMTConCommTier.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConCommTier::Release](../../../../Configuration-Interfaces/Groups/IMTConCommTier/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-groups-grouptotal-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupTotal.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupTotal

[Previous](GroupUnsubscribe.md) | [Next](GroupNext.md)

# IMTGatewayAPI::GroupTotal

Get the number of the groups configurations available for a gateway.

C++
    
    
    UINT  IMTGatewayAPI::GroupTotal()

.NET
    
    
    uint  CIMTGatewayAPI.GroupTotal()

### Return Value

The number of group configurations .

### Note

This method is used only for gateways.

```

---

<a id='main-interface-configuration-databases-groups-groupunsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Groups/GroupUnsubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Groups](../Groups.md) / GroupUnsubscribe

[Previous](GroupSubscribe.md) | [Next](GroupTotal.md)

# IMTGatewayAPI::GroupUnsubscribe

Unsubscribe from events and hooks associated with the groups configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GroupUnsubscribe(
       IMTConGroupSink*  sink      // A pointer to the IMTConGroupSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GroupUnsubscribe(
       CIMTConGroupSink  sink      // CIMTConGroupSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConGroupSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This is a pair method to [IMTGatewayAPI::GroupSubscribe](GroupSubscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) error is returned.

```

---

<a id='main-interface-configuration-databases-network-netservercreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerCreate

[Previous](../Network.md) | [Next](NetServerRangeCreate.md)

# IMTGatewayAPI::NetServerCreate

Create an object of configuration of the platform components.

C++
    
    
    IMTConServer*  IMTGatewayAPI::NetServerCreate()

.NET
    
    
    CIMTConServer  CIMTGatewayAPI.NetServerCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConServer](../../../../Configuration-Interfaces/Network/IMTConServer.md) interface. In case of failure, it returns Null.

### Note

The created object must be deleted by calling the [IMTConServer::Release](../../../../Configuration-Interfaces/Network/IMTConServer/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-network-netserverget-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerGet.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerGet

[Previous](NetServerNext.md) | [Next](../Spreads.md)

# IMTGatewayAPI::NetServerGet

Get a server configuration by the ID.

C++
    
    
    MTAPIRES  IMTGatewayAPI::NetServerGet(
       const UINT64   id,         // ID
       IMTConServer*  config      // Comment
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.NetServerGet(
       ulong          id,         // ID
       CIMTConServer  config      // Comment
       )

### Parameters

**id**  
[in] Server ID.

**config**  
[out] The server configuration object. The config object must first be created using theIMTGatewayAPI::NetServerCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The [IMTConServer::Id()](../../../../Configuration-Interfaces/Network/IMTConServer/Id.md) value is used as the ID.

```

---

<a id='main-interface-configuration-databases-network-netservernext-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerNext.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerNext

[Previous](NetServerTotal.md) | [Next](NetServerGet.md)

# IMTGatewayAPI::NetServerNext

Get a server configuration by the index.

C++
    
    
    MTAPIRES  IMTGatewayAPI::NetServerNext(
       const UINT     pos,        // Position of the configuration
       IMTConServer*  config      // Comment
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.NetServerNext(
       uint           pos,        // Position of the configuration
       CIMTConServer  config      // Comment
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

**config**  
[out] The server configuration object. The config object must first be created using theIMTGatewayAPI::NetServerCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This method copies the configuration data of a server with a specified index to the config object.

```

---

<a id='main-interface-configuration-databases-network-netserverrangecreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerRangeCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerRangeCreate

[Previous](NetServerCreate.md) | [Next](NetServerSubscribe.md)

# IMTGatewayAPI::NetServerRangeCreate

Create an object of the range of orders, deals or accounts.

C++
    
    
    IMTConServerRange*  IMTGatewayAPI::NetServerRangeCreate()

.NET
    
    
    CIMTConServerRange  CIMTGatewayAPI.NetServerRangeCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConServerRange](../../../../Configuration-Interfaces/Network/IMTConServerRange.md) interface. In case of failure, it returns Null.

### Note

The created object must be deleted by calling the [IMTConServerRange::Release](../../../../Configuration-Interfaces/Network/IMTConServerRange/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-network-netserversubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerSubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerSubscribe

[Previous](NetServerRangeCreate.md) | [Next](NetServerUnsubscribe.md)

# IMTGatewayAPI::NetServerSubscribe

Subscribe to events associated with the configuration of the platform components.

C++
    
    
    MTAPIRES  IMTGatewayAPI::NetServerSubscribe(
       IMTConServerSink*  sink      // A pointer to the IMTConServerSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.NetServerSubscribe(
       CIMTConServerSink  sink      // CIMTConServerSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConServerSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same interface [IMTConServerSink](../../../../Configuration-Interfaces/Network/IMTConServerSink.md) cannot subscribe to an event twice - in this case the response code [MT_RET_ERR_DUPLICATE](../../../../Return-Codes/Common-errors.md) is returned.

```

---

<a id='main-interface-configuration-databases-network-netservertotal-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerTotal.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerTotal

[Previous](NetServerUnsubscribe.md) | [Next](NetServerNext.md)

# IMTGatewayAPI::NetServerTotal

The total number of server configurations available in the platform.

C++
    
    
    UINT  IMTGatewayAPI::NetServerTotal()

.NET
    
    
    uint  IMTGatewayAPI::NetServerTotal()

### Return Value

The number of server configurations in the trading platform.

```

---

<a id='main-interface-configuration-databases-network-netserverunsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Network/NetServerUnsubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Network](../Network.md) / NetServerUnsubscribe

[Previous](NetServerSubscribe.md) | [Next](NetServerTotal.md)

# IMTGatewayAPI::NetServerUnsubscribe

Unsubscribe from events associated with the configuration of the platform components.

C++
    
    
    MTAPIRES  IMTGatewayAPI::NetServerUnsubscribe(
       IMTConServerSink*  sink      // A pointer to the IMTConServerSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.NetServerUnsubscribe(
       CIMTConServerSink  sink      // CIMTConServerSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConServerSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This method is pared to [IMTGatewayAPI::NetServerSubscribe](NetServerSubscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) error is returned.

```

---

<a id='main-interface-configuration-databases-spreads-spreadadd-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadAdd.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadAdd

[Previous](SpreadUnsubscribe.md) | [Next](SpreadDelete.md)

# IMTGatewayAPI::SpreadAdd

Add or update a spread configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadAdd(
       IMTSpreadSymbol*  spread      // Spread configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadAdd(
       CIMTSpreadSymbol  spread      // Spread configuration object
       )

### Parameters

**spread**  
[in] Spread configuration object.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

When calling the method, a check is made whether the entry already exists. If the entry already exists, it is updated, otherwise a new entry is added. A key field for comparison is [IMTConSpread::ID](../../../../Configuration-Interfaces/Spreads/IMTConSpread/ID.md). When trying to add a record with an identical ID, no changes are made, and therefore [IMTConSpreadSink::OnSpreadUpdate](../../../../Configuration-Interfaces/Spreads/IMTConSpreadSink/OnSpreadUpdate.md) notification method is not called.

```

---

<a id='main-interface-configuration-databases-spreads-spreadcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadCreate

[Previous](../Spreads.md) | [Next](SpreadLegCreate.md)

# IMTGatewayAPI::SpreadCreate

Create an object of the configuration of a spread.

C++
    
    
    IMTConSpread*  IMTGatewayAPI::SpreadCreate()

.NET
    
    
    CIMTConSpread  CIMTGatewayAPI.SpreadCreate()

### Return Value

It returns a pointer to the created object that implements [IMTConSpread](../../../../Configuration-Interfaces/Spreads/IMTConSpread.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling [IMTConSpread::Release](../../../../Configuration-Interfaces/Spreads/IMTConSpread/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-spreads-spreaddelete-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadDelete.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadDelete

[Previous](SpreadAdd.md) | [Next](SpreadShift.md)

# IMTGatewayAPI::SpreadDelete

Deleting a spread configuration by the index.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadDelete(
       const UINT  pos      // Position of the configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadDelete(
       uint        pos      // Position of the configuration
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

A configuration can be deleted only from the plugins that run on the main server. For all other plugins the response code [MT_RET_ERR_NOTMAIN](../../../../Return-Codes/API.md) will be returned. If the object is not found, the response code [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) will be returned.

```

---

<a id='main-interface-configuration-databases-spreads-spreadget-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadGet.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadGet

[Previous](SpreadNext.md) | [Next](../../Trade-Databases.md)

# IMTGatewayAPI::SpreadGet

Receiving a spread configuration by the identifier.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadGet(
       UINT           id,         // Configuration name
       IMTConSpread*  spread      // Spread configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadGet(
       uint           id,         // Configuration name
       CIMTConSpread  spread      // Spread configuration object
       )

### Parameters

**id**  
[in]Configuration identifier.

**spread**  
[out] Spread configuration object. The spread object must be first created usingIMTServerAPI::SpreadCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

[IMTConSpread::ID](../../../../Configuration-Interfaces/Spreads/IMTConSpread/ID.md) value is used as the identifier.

```

---

<a id='main-interface-configuration-databases-spreads-spreadlegcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadLegCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadLegCreate

[Previous](SpreadCreate.md) | [Next](SpreadSubscribe.md)

# IMTGatewayAPI::SpreadLegCreate

Create an object of the configuration of a spread leg.

C++
    
    
    IMTConSpreadLeg*  IMTGatewayAPI::SpreadLegCreate()

.NET
    
    
    CIMTConSpreadLeg  CIMTGatewayAPI.SpreadLegCreate()

### Return Value

It returns a pointer to the created object that implements [IMTConSpreadLeg](../../../../Configuration-Interfaces/Spreads/IMTConSpreadLeg.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling [IMTConSpreadLeg::Release](../../../../Configuration-Interfaces/Spreads/IMTConSpreadLeg/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-spreads-spreadnext-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadNext.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadNext

[Previous](SpreadTotal.md) | [Next](SpreadGet.md)

# IMTGatewayAPI::SpreadNext

Receiving a spread configuration by the index.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadNext(
       const UINT     pos,        // Position of the configuration
       IMTConSymbol*  spread      // Spread configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadNext(
       uint           pos,        // Position of the configuration
       CIMTConSymbol  spread      // Spread configuration object
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

**spread**  
[out] Spread configuration object. The spread object must be first created usingIMTServerAPI::SpreadCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This method copies the configuration data of a spread with a specified index to spread object.

```

---

<a id='main-interface-configuration-databases-spreads-spreadshift-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadShift.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadShift

[Previous](SpreadDelete.md) | [Next](SpreadTotal.md)

# IMTGatewayAPI::SpreadShift

Change the position of a spread configuration in the list.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadShift(
       const UINT  pos,       // Position of the configuration
       const int   shift      // Shift
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadShift(
       uint        pos,       // Position of the configuration
       int         shift      // Shift
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

**shift**  
[in] Shift of the configuration relative to its current position. A negative value means the shift to the top of the list, a positive value - to its end.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The position of a configuration can be changed only from the plugins that run on the main server. For all other plugins the response code [MT_RET_ERR_NOTMAIN](../../../../Return-Codes/API.md) will be returned.

```

---

<a id='main-interface-configuration-databases-spreads-spreadsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadSubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadSubscribe

[Previous](SpreadLegCreate.md) | [Next](SpreadUnsubscribe.md)

# IMTGatewayAPI::SpreadSubscribe

Subscribe to events and hooks associated with the configuration of spreads.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadSubscribe(
       IMTConSpreadSink*  sink      // pointer to IMTConSpreadSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadSubscribe(
       CIMTConSpreadSink  sink      // CIMTConSpreadSink object
       )

### Parameters

**sink**  
[in] Pointer to the object that implementsIMTConSpreadSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same [IMTConSpreadSink](../../../../Configuration-Interfaces/Spreads/IMTConSpreadSink.md) interface cannot subscribe to an event twice - in this case, [MT_RET_ERR_DUPLICATE](../../../../Return-Codes/Common-errors.md) response code is returned.

```

---

<a id='main-interface-configuration-databases-spreads-spreadtotal-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadTotal.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadTotal

[Previous](SpreadShift.md) | [Next](SpreadNext.md)

# IMTGatewayAPI::SpreadTotal

The total number of spread configurations available in the platform.

C++
    
    
    UINT  IMTGatewayAPI::SpreadTotal()

.NET
    
    
    uint  CIMTGatewayAPI.SpreadTotal()

### Return Value

The number of configurations of spreads in the trading platform.

```

---

<a id='main-interface-configuration-databases-spreads-spreadunsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Spreads/SpreadUnsubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Spreads](../Spreads.md) / SpreadUnsubscribe

[Previous](SpreadSubscribe.md) | [Next](SpreadAdd.md)

# IMTGatewayAPI::SpreadUnsubscribe

Unsubscribe from events and hooks associated with spread configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SpreadUnsubscribe(
       IMTConSpreadSink*  sink      // pointer to IMTConSpreadSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SpreadUnsubscribe(
       CIMTConSpreadSink  sink      // CIMTConSpreadSink object
       )

### Parameters

**sink**  
[in] Pointer to the object that implementsIMTConSymbolSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This is a pair method to [IMTGatewayAPI::SpreadSubscribe](SpreadSubscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) error is returned.

```

---

<a id='main-interface-configuration-databases-symbols-symboladdpreliminary-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolAddPreliminary.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolAddPreliminary

[Previous](SymbolUnsubscribe.md) | [Next](SymbolUpdate.md)

# IMTGatewayAPI::SymbolAddPreliminary

Add or update a preliminary configuration of a symbol.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolAddPreliminary(
       IMTConSymbol*  symbol      // An object of the symbol configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolAddPreliminary(
       CIMTConSymbol  symbol      // An object of the symbol configuration
       )

### Parameters

**symbol**  
[in] An object of the symbol configuration.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

## Symbol Adding Features

Process of the importing the symbols into the trading platform using this method has several peculiarities:

  * When calling the method, a check is made whether the entry already exists. If the entry already exists, it is updated (the list of parameters that can be updated is given below), otherwise a new entry is added. A key field for comparison is the name of the symbol [IMTConSymbol::Symbol()](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Symbol.md). When you try to add a completely identical record, no changes are made, and therefore the [IMTConSymbolSink::OnSymbolUpdate](../../../../Configuration-Interfaces/Symbols/IMTConSymbolSink/OnSymbolUpdate.md) notification method is not called.
  * All symbols are added to the \Preliminary\ symbols subgroup. For example, if the path 'Metals\Gold' ([IMTConSymol::Path](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Path.md)) is indicated in the added symbol parameter, the symbol will be added to the \Preliminary\Metals\Gold group.
  * All symbols are imported with the trading possibility ([IMTConSymbol::TradeMode](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TradeMode.md)) turned off.



Therefore, an administrator has to manually place a symbol into an appropriate group after the import and allow trading for it.

> For full control over symbols, use [IMTGatewayAPI::SymbolUpdate](SymbolUpdate.md) method. It allows adding symbols to any group and changing any symbol parameters.

The below list includes all the symbol parameters that can be changed using this method. Other parameters cannot be modified.

  * [ISIN](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/ISIN.md)
  * [Description](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Description.md)
  * [International](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/International.md)
  * [Basis](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Basis.md)
  * [Source](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md)
  * [Page](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Page.md)
  * [CurrencyBase](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/CurrencyBase.md)
  * [CurrencyProfit](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/CurrencyProfit.md)
  * [CurrencyMargin](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/CurrencyMargin.md)
  * [Color](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Color.md)
  * [ColorBackground](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/ColorBackground.md)
  * [TickFlags](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TickFlags.md)
  * [TickBookDepth](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TickBookDepth.md)
  * [FilterDiscard](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/FilterDiscard.md)
  * [FilterSoft](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/FilterSoft.md)
  * [FilterSoftTicks](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/FilterSoftTicks.md)
  * [FilterHard](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/FilterHard.md)
  * [FilterHardTicks](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/FilterHardTicks.md)
  * [TradeFlags](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TradeFlags.md)
  * [Spread](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Spread.md)
  * [SpreadBalance](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/SpreadBalance.md)
  * [TickValue](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TickValue.md)
  * [TickSize](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TickSize.md)
  * [ContractSize](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/ContractSize.md)
  * [GTCMode](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/GTCMode.md)
  * [CalcMode](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/CalcMode.md)
  * [QuotesTimeout](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/QuotesTimeout.md)
  * [PriceSettle](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/PriceSettle.md)
  * [PriceLimitMax](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/PriceLimitMax.md)
  * [PriceLimitMin](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/PriceLimitMin.md)
  * [TimeStart](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TimeStart.md)
  * [TimeExpiration ](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/TimeExpiration.md)
  * [FillFlags](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/FillFlags.md)
  * [ExpirFlags](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/ExpirFlags.md)
  * [VolumeMin](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/VolumeMin.md)
  * [VolumeMax](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/VolumeMax.md)
  * [VolumeStep](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/VolumeStep.md)
  * [VolumeLimit ](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/VolumeLimit.md)
  * [MarginCheckMode](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginFlags.md)
  * [MarginInitial](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginInitial.md)
  * [MarginMaintenance](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginMaintenance.md)
  * [MarginLong](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginLong.md)
  * [MarginShort](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginShort.md)
  * [MarginLimit](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginLimit.md)
  * [MarginStop](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginStop.md)
  * [MarginStopLimit](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/MarginStopLimit.md)



```

---

<a id='main-interface-configuration-databases-symbols-symbolcreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolCreate

[Previous](../Symbols.md) | [Next](SymbolSessionCreate.md)

# IMTGatewayAPI::SymbolCreate

Create an object of the symbol configuration.

C++
    
    
    IMTConSymbol*  IMTGatewayAPI::SymbolCreate()

.NET
    
    
    CIMTConSymbol  CIMTGatewayAPI.SymbolCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConSymbol](../../../../Configuration-Interfaces/Symbols/IMTConSymbol.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConSymbol::Release](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-symbols-symboldelete-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolDelete.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolDelete

[Previous](SymbolUpdate.md) | [Next](SymbolTotal.md)

# IMTGatewayAPI::SymbolDelete

Delete a symbol configuration by the index or name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolDelete(
       LPCWSTR  name      // Symbol name
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolDelete(
       string   name      // Symbol name
       )

### Parameters

**name**  
[in] Symbol name.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

If the object is not found, the response code [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) is returned.

```

---

<a id='main-interface-configuration-databases-symbols-symbolget-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolGet.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolGet

[Previous](SymbolNext.md) | [Next](../Groups.md)

<a id="group"></a>
# IMTGatewayAPI::SymbolGet (#group)

Gets the symbol configuration by the name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolGet(
       LPCWSTR        name,       // Name of the configuration
       IMTConSymbol*  symbol      // An object of the symbol configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolGet(
       string         name,       // Name of the configuration
       CIMTConSymbol  symbol      // An object of the symbol configuration
       )

<a id="parameters"></a>
### Parameters (#parameters)

**name**  
[in] The name of the configuration.

**symbol**  
[out] An object of the symbol configuration. The symbol object must be first created using theIMTGatewatAPI::SymbolCreatemethod.

<a id="return-value"></a>
### Return Value (#return-value)

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

<a id="note"></a>
### Note (#note)

The method returns a symbol configuration with default trade settings.

  * If a symbol with the name matching the symbol name in the external system is found in the platform, SymbolGet will return the configuration of the original symbol.
  * If there is no such symbol in the platform, the first translation setting corresponding to the original symbol will be used. For example, if for the original EURUSD symbol two settings are available, EURUSD.1 and EURUSD.2, SymbolGet(EURUSD,symbol) will return the configuration of EURUSD.1.
  * During the call of SymbolGet(name,group,symbol), the availability of a symbol for the group is additionally checked. If a symbol with the original name exists in the platform and it is available to the specified group, the method will return its configuration. Otherwise, a symbol from the first translation setting corresponding to the original symbol will be used. If it is available to the specified group, the method will return its settings. If it is not available, the next setting will be used, etc.



<a id="group"></a>
# IMTGatewayAPI::SymbolGet (#group)

Get symbol settings taking into account that they are overridden for the specified group.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolGet(
       LPCWSTR             name,        // Name of the configuration
       LPCWSTR             name_group,  // Group name
       IMTConSymbol*       symbol       // An object of the symbol configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolGet(
       string              name,        // Name of the configuration
       string              name_group,  // Group name
       CIMTConSymbol       symbol       // An object of the symbol configuration
       )

<a id="parameters"></a>
### Parameters (#parameters)

**name**  
[in] The name of the configuration.

**name_group**  
[in] Group name.

**symbol**  
[out] An object of the symbol configuration. The symbol object must be first created using theIMTGatewatAPI::SymbolCreatemethod.

<a id="return-value"></a>
### Return Value (#return-value)

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

<a id="note"></a>
### Note (#note)

The method returns a symbol configuration with trade settings for the specified group. The [IMTConGroup::Group](../../../../Configuration-Interfaces/Groups/IMTConGroup/Group.md) value is used as the group name.

  * If a symbol with the name matching the symbol name in the external system is found in the platform, SymbolGet will return the configuration of the original symbol.
  * If there is no such symbol in the platform, the first translation setting corresponding to the original symbol will be used. For example, if for the original EURUSD symbol two settings are available, EURUSD.1 and EURUSD.2, SymbolGet(EURUSD,symbol) will return the configuration of EURUSD.1.
  * During the call of SymbolGet(name,group,symbol), the availability of a symbol for the group is additionally checked. If a symbol with the original name exists in the platform and it is available to the specified group, the method will return its configuration. Otherwise, a symbol from the first translation setting corresponding to the original symbol will be used. If it is available to the specified group, the method will return its settings. If it is not available, the next setting will be used, etc.



```

---

<a id='main-interface-configuration-databases-symbols-symbolnext-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolNext.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolNext

[Previous](SymbolTotal.md) | [Next](SymbolGet.md)

# IMTGatewayAPI::SymbolNext

Get the symbol configuration by the index.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolNext(
       const UINT     pos,        // Position of the configuration
       IMTConSymbol*  symbol      // An object of the symbol configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolNext(
       uint           pos,        // Position of the configuration
       CIMTConSymbol  symbol      // An object of the symbol configuration
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

**symbol**  
[out] An object of the symbol configuration. The symbol object must be first created using theIMTGatewayAPI::SymbolCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method copies the configuration data of a symbol with a specified index to the symbol object.

  * Symbols with the filled [IMTConSymbol::Source](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md) field. Quotes for such symbols are always provided by the source symbol.
  * Symbols with the disabled [IMTConSymbol::EnTickFlags::TICK_REALTIME (#entickflags)](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags) flag. The platform does not receive quotes from gateways and datafeeds for such symbols.



```

---

<a id='main-interface-configuration-databases-symbols-symbolsessioncreate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolSessionCreate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolSessionCreate

[Previous](SymbolCreate.md) | [Next](SymbolSubscribe.md)

# IMTGatewayAPI::SymbolSessionCreate

Create an object of configuration of a trading or quoting session of the symbol.

C++
    
    
    IMTConSymbolSession*  IMTGatewayAPI::SymbolSessionCreate()

.NET
    
    
    CIMTConSymbolSession  CIMTGatewayAPI.SymbolSessionCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConSymbolSession](../../../../Configuration-Interfaces/Symbols/IMTConSymbolSession.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConSymbolSession::Release](../../../../Configuration-Interfaces/Symbols/IMTConSymbolSession/Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-symbols-symbolsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolSubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolSubscribe

[Previous](SymbolSessionCreate.md) | [Next](SymbolUnsubscribe.md)

# IMTGatewayAPI::SymbolSubscribe

Subscribe to events and hooks associated with the configuration of symbols.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolSubscribe(
       IMTConSymbolSink*  sink      // A pointer to the IMTConSymbolSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolSubscribe(
       CIMTConSymbolSink  sink      // CIMTConSymbolSink object
       )

### Parameters

**sink**  
[in] Pointer to the object that implementsIMTConSymbolSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same interface [IMTConSymbolSink](../../../../Configuration-Interfaces/Symbols/IMTConSymbolSink.md) cannot subscribe to an event twice - in this case the response code [MT_RET_ERR_DUPLICATE](../../../../Return-Codes/Common-errors.md) is returned.

```

---

<a id='main-interface-configuration-databases-symbols-symboltotal-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolTotal.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolTotal

[Previous](SymbolDelete.md) | [Next](SymbolNext.md)

# IMTGatewayAPI::SymbolTotal

Get the number of the symbols configurations avaialble for a gateway or a data feed.

C++
    
    
    UINT  IMTGatewayAPI::SymbolTotal()

.NET
    
    
    uint  CIMTGatewayAPI.SymbolTotal()

### Return Value

The number of configurations, 

### Note

Available symbols are specified in the "Symbols" tab of a gateway in MetaTrader 5 Administrator. The list does not include the symbols, for which sending of quotes from the gateway is useless:

  * Symbols with the filled [IMTConSymbol::Source](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Source.md) field. Quotes for such symbols are always provided by the source symbol.
  * Symbols with the disabled [IMTConSymbol::EnTickFlags::TICK_REALTIME (#entickflags)](../../../../Configuration-Interfaces/Symbols/IMTConSymbol/Enumerations.md#entickflags) flag. The platform does not receive quotes from gateways and datafeeds for such symbols.



```

---

<a id='main-interface-configuration-databases-symbols-symbolunsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolUnsubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolUnsubscribe

[Previous](SymbolSubscribe.md) | [Next](SymbolAddPreliminary.md)

# IMTGatewayAPI::SymbolUnsubscribe

Unsubscribe from events and hooks associated with the configuration of symbols.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolUnsubscribe(
       IMTConSymbolSink*  sink      // A pointer to the IMTConSymbolSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolUnsubscribe(
       CIMTConSymbolSink  sink      // CIMTConSymbolSink object
       )

### Parameters

**sink**  
[in] Pointer to the object that implementsIMTConSymbolSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This is a pair method to [IMTGatewayAPI::SymbolSubscribe](SymbolSubscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) error is returned.

```

---

<a id='main-interface-configuration-databases-symbols-symbolupdate-md'></a>
### 195. `Main-Interface/Configuration-Databases/Symbols/SymbolUpdate.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Symbols](../Symbols.md) / SymbolUpdate

[Previous](SymbolAddPreliminary.md) | [Next](SymbolDelete.md)

# IMTGatewayAPI::SymbolUpdate

Add or update a symbol configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SymbolUpdate(
       IMTConSymbol*  symbol      // An object of the symbol configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SymbolUpdate(
       CIMTConSymbol  symbol      // An object of the symbol configuration
       )

### Parameters

**symbol**  
[in] An object of the symbol configuration.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, a corresponding error code will be returned.

### Note

The method can only be called after receiving the [IMTGatewaySink::OnServerSynchronized](../../../Event-Interface/OnServerSynchronized.md) notification for the main trade server. Otherwise, the call will return the [MT_RET_OK_NONE](../../../../Return-Codes/Successful-completion.md) error.

```

---

<a id='main-interface-configuration-databases-time-create-md'></a>
### 195. `Main-Interface/Configuration-Databases/Time/Create.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Time](../Time.md) / Create

[Previous](../Time.md) | [Next](Subscribe.md)

# IMTGatewayAPI::TimeCreate

Create an object of the time configuration.

C++
    
    
    IMTConTime*  IMTGatewayAPI::TimeCreate()

.NET
    
    
    CIMTConTime  CIMTGatewayAPI.TimeCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConTime](../../../../Configuration-Interfaces/Time/IMTCon.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConTime::Release](../../../../Configuration-Interfaces/Time/IMTConTime/IMTCon-Release.md) method of this object.

```

---

<a id='main-interface-configuration-databases-time-current-md'></a>
### 195. `Main-Interface/Configuration-Databases/Time/Current.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Time](../Time.md) / Current

[Previous](Unsubscribe.md) | [Next](Get.md)

# IMTGatewayAPI::TimeCurrent

Get the current trading time.

C++
    
    
    INT64  IMTGatewayAPI::TimeCurrent()

.NET
    
    
    long  CIMTGatewayAPI.TimeCurrent()

### Return Value

The current trading time of the platform - the number of seconds elapsed since 01.01.1970.

### Note

The method returns time taking into account the /timezone and /timecorrect parameters, which are passed [in a command line when the gateway/datafeed is started](../../../Exported-Functions/MTGatewayCreateLocal.md). 

  * When a gateway/datafeed is started by the history server, the values of the /timezone and /timecorrect parameters are set in accordance with time settings on the trade server ([IMTConTime](../../../../Configuration-Interfaces/Time/IMTCon.md)).
  * When a gateway/datafeed is started as a service (remote gateway), these parameters should be specified by the user. If these parameters are not set, IMTGatewayAPI::TimeCurrent will pass time in the UTC+0 time zone.



```

---

<a id='main-interface-configuration-databases-time-get-md'></a>
### 195. `Main-Interface/Configuration-Databases/Time/Get.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Time](../Time.md) / Get

[Previous](Current.md) | [Next](../Network.md)

# IMTGatewayAPI::TimeGet

Get the time configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::TimeGet(
       IMTConTime*  config      // An object of time configuration
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.TimeGet(
       CIMTConTime  config      // An object of time configuration
       )

### Parameters

**config**  
[out] An object of the time configuration. The config object must first be created using theIMTGatewayAPI::TimeCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The [MT_RET_OK_NONE](../../../../Return-Codes/Successful-completion.md) response means that the time settings have not been yet initialized on the Gateway API side. Time settings can only be requested after receiving the [IMTGatewaySink::OnGatewayStart](../../../Event-Interface/OnGatewayStart.md) event.

```

---

<a id='main-interface-configuration-databases-time-subscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Time/Subscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Time](../Time.md) / Subscribe

[Previous](Create.md) | [Next](Unsubscribe.md)

# IMTGatewayAPI::TimeSubscribe

Subscribe to events and hooks associated with the time configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::TimeSubscribe(
       IMTConTimeSink*  sink      // A pointer to the IMTConTimeSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.TimeSubscribe(
       CIMTConTimeSink  sink      // CIMTConTimeSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConTimeSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same interface [IMTConTimeSink](../../../../Configuration-Interfaces/Time/IMTConSink.md) cannot subscribe to an event twice - in this case the response code [MT_RET_ERR_DUPLICATE](../../../../Return-Codes/Common-errors.md) is returned.

```

---

<a id='main-interface-configuration-databases-time-unsubscribe-md'></a>
### 195. `Main-Interface/Configuration-Databases/Time/Unsubscribe.md`

```markdown
[🏠 Document Start](../../../../README.md) / [Gateway API](../../../README.md) / [Main Interface](../../../Main-Interface.md) / [Configuration Databases](../../Configuration-Databases.md) / [Time](../Time.md) / Unsubscribe

[Previous](Subscribe.md) | [Next](Current.md)

# IMTGatewayAPI::TimeUnsubscribe

Unsubscribe from events and hooks associated with the time configuration.

C++
    
    
    MTAPIRES  IMTGatewayAPI::TimeUnsubscribe(
       IMTConTimeSink*  sink      // A pointer to the IMTConTimeSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.TimeUnsubscribe(
       CIMTConTimeSink  sink      // CIMTConTimeSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTConTimeSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This is a pair method to [IMTGatewayAPI::TimeSubscribe](Subscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../../Return-Codes/Common-errors.md) error is returned.

```

---

<a id='main-interface-controlling-orders-in-external-system-gatewayorderarraycreate-md'></a>
### 195. `Main-Interface/Controlling-Orders-in-External-System/GatewayOrderArrayCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Controlling Orders in External System](../Controlling-Orders-in-External-System.md) / GatewayOrderArrayCreate

[Previous](../Controlling-Orders-in-External-System.md) | [Next](GatewayOrdersAnswer.md)

# IMTGatewayAPI::GatewayOrderArrayCreate

Create an object of the array of positions.

C++
    
    
    IMTOrderArray*  IMTGatewayAPI::GatewayOrderArrayCreate()

.NET
    
    
    CIMTOrderArray  CIMTGatewayAPI.GatewayOrderArrayCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTOrderArray](../../../Database-Interfaces/Trade/Orders/IMTOrderArray.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling [IMTOrderArray::Release](../../../Database-Interfaces/Trade/Orders/IMTOrderArray/Release.md) method of this object.

```

---

<a id='main-interface-controlling-orders-in-external-system-gatewayordersanswer-md'></a>
### 195. `Main-Interface/Controlling-Orders-in-External-System/GatewayOrdersAnswer.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Controlling Orders in External System](../Controlling-Orders-in-External-System.md) / GatewayOrdersAnswer

[Previous](GatewayOrderArrayCreate.md) | [Next](../Synchronizing-Trading-Data.md)

# IMTGatewayAPI::GatewayOrdersAnswer

The method is used to display in MetaTrader 5 Administrator the client's current pending orders placed at the external trading system.

The functionality is currently under development.  
---  
      
    
    MTAPIRES  IMTGatewayAPI::GatewayOrdersAnswer(
       const MTAPIRES          result,           // Result
       const INT64*            orders_time,      // Order fixing time
       const IMTOrderArray*    orders            // Array of orders
       )

### Parameters

**result**  
[in] MT_RET_OK response code is used if data on positions has been successfully received from an external system. Otherwise, the appropriateerror codeis to be returned.

**orders_time**  
[in] Orders state fixing time, specified in seconds that have elapsed since 01.01.1970.

**orders**  
[in]An object of the array of ordersreceived from an external system.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### 

```

---

<a id='main-interface-controlling-positions-in-external-system-gatewayparamarraycreate-md'></a>
### 195. `Main-Interface/Controlling-Positions-in-External-System/GatewayParamArrayCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Controlling Positions in External System](../Controlling-Positions-in-External-System.md) / GatewayParamArrayCreate

[Previous](../Controlling-Positions-in-External-System.md) | [Next](GatewayPositionArrayCreate.md)

# IMTGatewayAPI::GatewayParamArrayCreate

Create an object of the array of parameters.

C++
    
    
    IMTConParamArray*  IMTGatewayAPI::GatewayParamArrayCreate()

.NET
    
    
    CIMTConParamArray  CIMTGatewayAPI.GatewayParamArrayCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConParamArray](../../../Configuration-Interfaces/Additional-Parameters/IMTConParamArray.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConParamArray::Release](../../../Configuration-Interfaces/Additional-Parameters/IMTConParamArray/Release.md) method of this object.

```

---

<a id='main-interface-controlling-positions-in-external-system-gatewaypositionarraycreate-md'></a>
### 195. `Main-Interface/Controlling-Positions-in-External-System/GatewayPositionArrayCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Controlling Positions in External System](../Controlling-Positions-in-External-System.md) / GatewayPositionArrayCreate

[Previous](GatewayParamArrayCreate.md) | [Next](GatewayPositionsAnswer.md)

# IMTGatewayAPI::GatewayPositionArrayCreate

Create an object of the array of positions.

C++
    
    
    IMTPositionArray*  IMTGatewayAPI::GatewayPositionArrayCreate()

.NET
    
    
    CIMTPositionArray  CIMTGatewayAPI.GatewayPositionArrayCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTPositionArray](../../../Database-Interfaces/Trade/Positions/IMTPositionArray.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTPositionArray::Release](../../../Database-Interfaces/Trade/Positions/IMTPositionArray.md) method of this object.

```

---

<a id='main-interface-controlling-positions-in-external-system-gatewaypositionsanswer-md'></a>
### 195. `Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsAnswer.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Controlling Positions in External System](../Controlling-Positions-in-External-System.md) / GatewayPositionsAnswer

[Previous](GatewayPositionArrayCreate.md) | [Next](GatewayPositionsCheck.md)

# IMTGatewayAPI::GatewayPositionsAnswer

The method is used to display positions on the accounts in MetaTrader 5 Administrator, which are used by the gateway in an external trading system. After calling [IMTGatewaySink:HookGatewayPositionsRequest](../../Event-Interface/HookGatewayPositionsRequest.md) hook, a developer can transfer positions state to MetaTrader 5 platform using this method. Transferred positions are displayed in "Positions" tab of MetaTrader 5 Administrator.

More data on using this method can be found in [IMTGatewaySink:HookGatewayPositionsRequest](../../Event-Interface/HookGatewayPositionsRequest.md) hook description.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewayPositionsAnswer(
       const MTAPIRES          result,           // Result
       const INT64*            positions_time,  // Position state fixing time
       const IMTPositionArray* positions        // Positions array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewayPositionsAnswer(
       MTRetCode               result,           // Result
       long                    positions_time,   // Position state fixing time
       CIMTPositionArray       positions         // Positions array
       )

### Parameters

**result**  
[in] MT_RET_OK response code is used if data on positions has been successfully received from an external system. Otherwise, the appropriateerror codeis to be returned.

**positions_time**  
[in] Positions state fixing time, specified in seconds that have elapsed since 01.01.1970. The time is displayed on "Positions" tab of the gateway of the administrator terminal.

**positions**  
[in]An object of the array of positionsreceived from an external system. These positions will be displayed on "Positions" tab of the gateway of the administrator terminal.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

To pass information about external positions the following field of an [IMTPosition](../../../Database-Interfaces/Trade/Positions/IMTPosition.md) object can be used:

  * [Symbol](../../../Database-Interfaces/Trade/Positions/IMTPosition/Symbol.md)
  * [Action](../../../Database-Interfaces/Trade/Positions/IMTPosition/Action.md)
  * [Digits](../../../Database-Interfaces/Trade/Positions/IMTPosition/Digits.md)
  * [PriceOpen](../../../Database-Interfaces/Trade/Positions/IMTPosition/PriceOpen.md)
  * [Volume](../../../Database-Interfaces/Trade/Positions/IMTPosition/Volume.md)
  * [Comment](../../../Database-Interfaces/Trade/Positions/IMTPosition/Comment.md)



```

---

<a id='main-interface-controlling-positions-in-external-system-gatewaypositionscheck-md'></a>
### 195. `Main-Interface/Controlling-Positions-in-External-System/GatewayPositionsCheck.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Controlling Positions in External System](../Controlling-Positions-in-External-System.md) / GatewayPositionsCheck

[Previous](GatewayPositionsAnswer.md) | [Next](../Controlling-Orders-in-External-System.md)

# IMTGatewayAPI::GatewayPositionsCheck

This method is intended for verification of positions with an external trading system. This method is reserved for future use.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewayPositionsCheck(
       const MTAPIRES          result,           // Result
       const INT64*            positions_time,  // Position state fixing time
       const IMTPositionArray* positions        // Positions array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewayPositionsCheck(
       MTRetCode               result,           // Result
       long                    positions_time,   // Position state fixing time
       CIMTPositionArray       positions         // Positions array
       )

### Parameters

**result**  
[in] Response code.

**positions_time**  
[in] Positions state fixing time, specified in seconds that have elapsed since 01.01.1970.

**positions**  
[in]An object of the array of positionsreceived from an external system. For a correct operation, the following fields ofIMTPositionobjects inside the array must be filled:

  * Symbol
  * Volume
  * ContractSize
  * Action
  * PriceOpen



### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='main-interface-external-connection-state-stateconnect-md'></a>
### 195. `Main-Interface/External-Connection-State/StateConnect.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [External Connection State](../External-Connection-State.md) / StateConnect

[Previous](../External-Connection-State.md) | [Next](StateTraffic.md)

# IMTGatewayAPI::StateConnect

Set the state of the gateway/data feed external connection.

C++
    
    
    MTAPIRES  IMTGatewayAPI::StateConnect(
       const UINT  state      // Connection state
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.StateConnect(
       bool        state      // Connection state
       )

### Parameters

**state**  
[in] Any value other than 0 means that external connection was established successfully. The 0 value means that connection is absent.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='main-interface-external-connection-state-statetraffic-md'></a>
### 195. `Main-Interface/External-Connection-State/StateTraffic.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [External Connection State](../External-Connection-State.md) / StateTraffic

[Previous](StateConnect.md) | [Next](../Client-Connection.md)

# IMTGatewayAPI::StateTraffic

Add the value to the external connection traffic counter.

C++
    
    
    MTAPIRES  IMTGatewayAPI::StateTraffic(
       const UINT  received_bytes,     // Incoming traffic
       const UINT  sent_bytes          // Outgoing traffic
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.StateTraffic(
       uint        received,           // Incoming traffic
       uint        sent                // Outgoing traffic
       )

### Parameters

**received_bytes**  
[in] Incoming traffic in bytes.

**sent_bytes**  
[in] Outgoing traffic in bytes.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Incoming and outgoing traffic values passed using this method are added to the current values.

```

---

<a id='main-interface-gateway-symbols-gatewaysymboladd-md'></a>
### 195. `Main-Interface/Gateway-Symbols/GatewaySymbolAdd.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Gateway Symbols](../Gateway-Symbols.md) / GatewaySymbolAdd

[Previous](../Gateway-Symbols.md) | [Next](GatewaySymbolDelete.md)

# IMTGatewayAPI::GatewaySymbolAdd

Adds a new symbol to the list of symbols available to the gateway.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewaySymbolAdd(
       IMTConSymbol*  symbol      // Symbol configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewaySymbolAdd(
       CIMTConSymbol  symbol      // Symbol configuration object
       )

### Parameters

**symbol**  
[in] An object of the symbol configuration.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method can only be called from gateways.

```

---

<a id='main-interface-gateway-symbols-gatewaysymbolclear-md'></a>
### 195. `Main-Interface/Gateway-Symbols/GatewaySymbolClear.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Gateway Symbols](../Gateway-Symbols.md) / GatewaySymbolClear

[Previous](GatewaySymbolDelete.md) | [Next](GatewaySymbolTotal.md)

# IMTGatewayAPI::GatewaySymbolClear

Clears the entire list of symbols available to the gateway.

C++
    
    
    void  IMTGatewayAPI::GatewaySymbolClear()

.NET
    
    
    void  CIMTGatewayAPI.GatewaySymbolClear()

### Note

The method can only be called from gateways.

```

---

<a id='main-interface-gateway-symbols-gatewaysymboldelete-md'></a>
### 195. `Main-Interface/Gateway-Symbols/GatewaySymbolDelete.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Gateway Symbols](../Gateway-Symbols.md) / GatewaySymbolDelete

[Previous](GatewaySymbolAdd.md) | [Next](GatewaySymbolClear.md)

# IMTGatewayAPI::GatewaySymbolDelete

Deletes a symbol from the list available to the gateway (by name).

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewaySymbolDelete(
       LPCWSTR  name      // Symbol name
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewaySymbolDelete(
       string   name      // Symbol name
       )

### Parameters

**name**  
[in] Symbol name.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method can only be called from gateways.

```

---

<a id='main-interface-gateway-symbols-gatewaysymbolget-md'></a>
### 195. `Main-Interface/Gateway-Symbols/GatewaySymbolGet.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Gateway Symbols](../Gateway-Symbols.md) / GatewaySymbolGet

[Previous](GatewaySymbolNext.md) | [Next](../Processing-Trade-Requests.md)

# IMTGatewayAPI::GatewaySymbolDelete

Gets the description of a symbol available to the gateway, by name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewaySymbolDelete(
       LPCWSTR        name,       // Configuration name
       IMTConSymbol*  symbol      // Symbol configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewaySymbolDelete(
       string         name,       // Configuration name
       CIMTConSymbol  symbol      // Symbol configuration object
       )

### Parameters

**name**  
[in] The name of the configuration.

**symbol**  
[out] An object of the symbol configuration. The symbol object must be previously created using theIMTGatewayAPI::SymbolCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method can only be called from gateways.

```

---

<a id='main-interface-gateway-symbols-gatewaysymbolnext-md'></a>
### 195. `Main-Interface/Gateway-Symbols/GatewaySymbolNext.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Gateway Symbols](../Gateway-Symbols.md) / GatewaySymbolNext

[Previous](GatewaySymbolTotal.md) | [Next](GatewaySymbolGet.md)

# IMTGatewayAPI::GatewaySymbolDelete

Gets the description of a symbol available to the gateway, by index.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewaySymbolDelete(
       const UINT     pos,        // Configuration position
       IMTConSymbol*  symbol      // Symbol configuration object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewaySymbolDelete(
       uint           pos,        // Configuration position
       CIMTConSymbol  symbol      // Symbol configuration object
       )

### Parameters

**pos**  
[in] Position of the configuration, starting with 0.

**symbol**  
[out] An object of the symbol configuration. The symbol object must be previously created using theIMTGatewayAPI::SymbolCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method can only be called from gateways.

```

---

<a id='main-interface-gateway-symbols-gatewaysymboltotal-md'></a>
### 195. `Main-Interface/Gateway-Symbols/GatewaySymbolTotal.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Gateway Symbols](../Gateway-Symbols.md) / GatewaySymbolTotal

[Previous](GatewaySymbolClear.md) | [Next](GatewaySymbolNext.md)

# IMTGatewayAPI::GatewaySymbolDelete

Gets the total number of symbols available to the gateway.

C++
    
    
    UINT  IMTGatewayAPI::GatewaySymbolDelete()

.NET
    
    
    uint  CIMTGatewayAPI.GatewaySymbolDelete()

### Return Value

The number of symbols 

### Note

The method can only be called from gateways.

```

---

<a id='main-interface-history-data-chartdelete-md'></a>
### 195. `Main-Interface/History-Data/ChartDelete.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [History Data](../History-Data.md) / ChartDelete

[Previous](ChartRequest.md) | [Next](ChartUpdate.md)

# IMTGatewayAPI::ChartDelete

Delete a bar by the symbol.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ChartDelete(
       LPCWSTR            symbol,           // Symbol
       const INT64*       bars_dates,       // Dates of bars to delete
       const UINT         bars_dates_total  // The number of bars to delete
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.ChartDelete(
       string             symbol,           // Symbol
       long[]             bars_dates        // Dates of bars to delete
       )

### Parameters

**symbol**  
[in] The symbol, for which you want to delete historical data.

**bars_dates**  
[in] An array of the dates of bars you want to delete. Dates are specified in seconds that have elapsed since 01.01.1970.

**bars_dates_total**  
[in] The number of bars to delete.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

```

---

<a id='main-interface-history-data-chartreplace-md'></a>
### 195. `Main-Interface/History-Data/ChartReplace.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [History Data](../History-Data.md) / ChartReplace

[Previous](ChartUpdate.md) | [Next](../Tick-Data.md)

# IMTGatewayAPI::ChartReplace

Full replacement of history data in the specified period with the passed data.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ChartReplace(
       LPCWSTR            symbol,         // Symbol
       const INT64        from,           // Beginning of the period
       const INT64        to,             // End of the period
       const MTChartBar*  bars,           // New bars
       const UINT         bars_total      // Number of new bars
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.ChartReplace(
       string             symbol,         // Number of new bars
       long               from,           // Beginning of the period
       long               to,             // End of the period
       MTChartBar[]       bars            // New bars
       )

### Parameters

**symbol**  
[in] The symbol, for which you want to update historical data.

**from**  
[in] The beginning of the period for which you need to replace data. The date is specified in seconds since January 1, 1970.

**to**  
[in] The date is specified in seconds that have elapsed since 01.01.1970. The date is specified in seconds since January 1, 1970.

**bars**  
[in] New bars, described by theMTChartBarstructure.

**bars_total**  
[in] The number of bars passed.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, a corresponding error code is returned.

### Note

This method totally replaces the history data in the specified time period with the data passed in the 'bars' parameter.

```

---

<a id='main-interface-history-data-chartrequest-md'></a>
### 195. `Main-Interface/History-Data/ChartRequest.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [History Data](../History-Data.md) / ChartRequest

[Previous](../History-Data.md) | [Next](ChartDelete.md)

# IMTGatewayAPI::ChartRequest

Request minute bars for a symbol.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ChartRequest(
       LPCWSTR       symbol,         // Symbol
       const INT64   from,           // Beginning of the period
       const INT64   to,             // End of the period
       MTChartBar*&  bars,           // Array of bars
       UINT&         bars_total      // Number of received bars
       )

.NET
    
    
    MTChartBar[]  CIMTGatewayAPI.ChartRequest(
       string        symbol,         // Symbol
       long          from,           // Beginning of the period
       long          to,             // End of the period
       out MTRetCode res             // Response code
       )

### Parameters

**symbol**  
[in] The symbol for which you want to request historical data (bars).

**from**  
[in] The beginning of the period for which you need to get data. The date is specified in seconds that have elapsed since 01.01.1970.

**to**  
[in] The end of the period for which you need to get data. The date is specified in seconds that have elapsed since 01.01.1970.

**bars**  
[out] An array of bars (MTChartBarstructures).

**bars_total**  
[out] The number of obtained bars.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

Price data is stored on the history server in the form of one minute bars. Larger timeframes are formed on a client side from the minute bars according to the following principle: bars from the first to the last second of a period are used for calculation. For example, a H1 bar for 13:00 consists of minute bars within the range from 13:00:00 to 13:59:59.

```

---

<a id='main-interface-history-data-chartupdate-md'></a>
### 195. `Main-Interface/History-Data/ChartUpdate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [History Data](../History-Data.md) / ChartUpdate

[Previous](ChartDelete.md) | [Next](ChartReplace.md)

# IMTGatewayAPI::ChartUpdate

Change historical data of a symbol.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ChartUpdate(
       LPCWSTR            symbol,         // Symbol
       const MTChartBar*  bars,           // Bars to change
       const UINT         bars_total      // The number of bars to change
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.ChartUpdate(
       string             symbol,         // Number of new bars
       MTChartBar[]       bars            // Bars to change
       )

### Parameters

**symbol**  
[in] The symbol, for which you want to update historical data.

**bars**  
[in] Bars you want to update, described by theMTChartBarstructure.

**bars_total**  
[in] The number of bars to update.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

If the open price of a bar ([MTChartBar.open](../../../Structures/MTChartBar.md)) passed in the structure is 0, the bar will be deleted.

```

---

<a id='main-interface-mail-database-mailcreate-md'></a>
### 195. `Main-Interface/Mail-Database/MailCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Mail Database](../Mail-Database.md) / MailCreate

[Previous](../Mail-Database.md) | [Next](MailSend.md)

# IMTGatewayAPI::MailCreate

Create an object of a message in the internal mail system.

C++
    
    
    IMTMail*  IMTGatewayAPI::MailCreate()

.NET
    
    
    CIMTMail  CIMTGatewayAPI.MailCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTMail](../../../Database-Interfaces/Mail-Database/IMTMail.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTMail::Release](../../../Database-Interfaces/Mail-Database/IMTMail/Release.md) method of this object.

```

---

<a id='main-interface-mail-database-mailsend-md'></a>
### 195. `Main-Interface/Mail-Database/MailSend.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Mail Database](../Mail-Database.md) / MailSend

[Previous](MailCreate.md) | [Next](../User-Settings.md)

# IMTGatewayAPI::MailSend

Send emails via the internal mail system.

C++
    
    
    MTAPIRES  IMTGatewayAPI::MailSend(
       IMTMail*  mail      // Mail object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.MailSend(
       CIMTMail  mail      // Mail object
       )

### Parameters

**mail**  
[in] Mail object. The mail object must first be created using theIMTGatewayAPI::MailCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

Before sending an email, its correctness is checked (presence of its [subject](../../../Database-Interfaces/Mail-Database/IMTMail/Subject.md), [recipient](../../../Database-Interfaces/Mail-Database/IMTMail/To.md) and [sender](../../../Database-Interfaces/Mail-Database/IMTMail/From.md)).

You can use macros in the email body, which allow substituting relevant data depending on the email recipient:

  * #LOGIN# — the email recipient's account number.
  * #USERNAME# — the email recipient's name.
  * #CURRENCY# — the email recipient's deposit currency.
  * #BALANCE# — the email recipient's current balance.
  * #CREDIT# — the recipient's credit amount.
  * #EQUITY# — the current equity amount on the recipient's account.
  * #MARGIN# — the amount of funds required to cover current open positions.
  * #MARGIN_FREE# — the free margin amount.
  * #MARGIN_LEVEL# — the percent ratio of required margin and account equity.


  * #LEVERAGE# — the recipient's current leverage amount.



```

---

<a id='main-interface-processing-trade-requests-dealeranswerasync-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerAnswerAsync.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerAnswerAsync

[Previous](DealerLockAsync.md) | [Next](DealerExecuteAsync.md)

# IMTGatewayAPI::DealerAnswerAsync

Return the results of the captured request processing.

C++
    
    
    MTAPIRES  IMTGatewayAPI::DealerAnswerAsync(
       IMTConfirm*  confirm      // Request confirmation object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.DealerAnswerAsync(
       CIMTConfirm  confirm      // Request confirmation object
       )

### Parameters

**confirm**  
[in]Request confirmation object.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

Each trade request can only be responded once using this method. The only exceptions are some [response codes](../../../Database-Interfaces/Trade/Trade-Requests/IMTConfirm/Requests-Retcode.md) (MT_RET_REQUEST_REQUOTE, MT_RET_REQUEST_PRICES) in Instant and Request [execution modes](../../../Configuration-Interfaces/Symbols/IMTConSymbol/ExecMode.md).

### An example of a response to a SL/TP activation request, if such a request should be processed on the exchange side
    
    
    //+------------------------------------------------------------------+
    //| SL/TP control on the exchange side                               |
    //+------------------------------------------------------------------+
    void CMTGatewayApp::PreAnswerExchangeNoSLTP(const IMTRequest* request)
      {
       IMTConfirm*   confirm={0};
       IMTExecution* execution={0};
       MTAPISTR      str={0};
       //--- Checks
       if(m_api_gateway)
         {
          confirm=m_api_gateway->DealerConfirmCreate();
          execution=m_api_gateway->DealerExecutionCreate();
         }
       else
         {
          ExtLogger.Out(MTLogErr, L"failed to create confirm and execution interface");
          return;
         }
       //--- Response to a client that the request has been accepted
       confirm->ID(request->ID());
       confirm->Retcode(MT_RET_REQUEST_PLACED);
       confirm->Volume(request->Volume());
       confirm->Price(request->PriceOrder());
       confirm->Comment(L"pre confirmed message by ExampleGateway");
       //--- Send a response, the order gets the 'started' state, response 10008 will be sent to the terminal
       if(m_api_gateway->DealerAnswerAsync(confirm)!=MT_RET_OK)
          ExtLogger.Out(MTLogErr, L"confirm preanswer for request failed. Preanswer: %s", confirm->Print(str));
       else
          ExtLogger.Out(MTLogErr, L"Confirm preanswer: %s", confirm->Print(str));
       //--- Inform the MetaTrader server that a new order request will be sent to the exchange
       execution->ID(request->ID());
       execution->Order(request->ResultOrder());
       execution->OrderType(request->Type());
       execution->OrderVolume(request->Volume());
       execution->OrderPrice(request->PriceOrder());
       execution->Action(IMTExecution::TE_ORDER_NEW_REQUEST);
       execution->OrderActivationFlags(IMTOrder::ACTIV_FLAGS_NO_SL | IMTOrder::ACTIV_FLAGS_NO_TP);
       //--- Send the first response about the execution to the platform, the order gets the 'request adding' state
       if(m_api_gateway->DealerExecuteAsync(execution)!=MT_RET_OK)
          ExtLogger.Out(MTLogErr, L"Send DealerExecuteAsync for request failed. Answer: %s", execution->Print(str));
       else
          ExtLogger.Out(MTLogErr, L"PreAnswer: %s", execution->Print(str));
        //--- Clear objects
        if(confirm)
           confirm->Release();
        if(execution)
           execution->Release();
      }
    //+------------------------------------------------------------------+

After that, signals about further SL/TP triggering will not be sent to the gateway. As soon as the request is processed by the exchange, send the trade execution to the platform to complete the deal:
    
    
    //+------------------------------------------------------------------+
    //| Close position by SL/TP when response from exchange is received  |
    //+------------------------------------------------------------------+
    void CMTGatewayApp::AnswerCloseWithoutRequest(void)
      {
       IMTExecution* execution={0};
       MTAPISTR      str={0};
       //--- Checks
       if(m_api_gateway)
          execution=m_api_gateway->DealerExecutionCreate();
       else
         {
          ExtLogger.Out(MTLogErr, L"failed to create execution interface");
          return;
         }
        //--- Fill the execution object (pass your values to it)
        execution->Clear();
        execution->Login(1000);
        execution->Symbol(L"EURUSD");
        execution->Position(25983);
        execution->DealAction(IMTDeal::DEAL_SELL);
        execution->DealVolume(10000);
        execution->DealVolumeRemaind(0);
        execution->DealPrice(0.75000);
        execution->Digits(5);
        execution->Action(IMTExecution::TE_DEAL_EXTERNAL);
        //--- 
        if(m_api_gateway->DealerExecuteAsync(execution)!=MT_RET_OK)
           ExtLogger.Out(MTLogErr, L"AnswerCloseWithoutRequest: send DealerExecuteAsync for request failed. Answer: %s", execution->Print(str));
        else
           ExtLogger.Out(MTLogErr, L"AnswerCloseWithoutRequest answer: %s", execution->Print(str));
        //--- Clear the object
        if (execution)
            execution->Release();
      }
    //+------------------------------------------------------------------+

```

---

<a id='main-interface-processing-trade-requests-dealerconfirmcreate-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerConfirmCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerConfirmCreate

[Previous](../Processing-Trade-Requests.md) | [Next](DealerExecutionCreate.md)

# IMTGatewayAPI::DealerConfirmCreate

Create request confirmation interface object.

C++
    
    
    IMTConfirm*  IMTGatewayAPI::DealerConfirmCreate()

.NET
    
    
    CIMTConfirm  CIMTGatewayAPI.DealerConfirmCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTConfirm](../../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTConfirm.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTConfirm::Release](../../../Database-Interfaces/Trade/Trade-Requests/IMTConfirm/Requests-Release.md) method of this object.

```

---

<a id='main-interface-processing-trade-requests-dealerexecuteasync-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerExecuteAsync.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerExecuteAsync

[Previous](DealerAnswerAsync.md) | [Next](../Controlling-Positions-in-External-System.md)

# IMTGatewayAPI::DealerExecuteAsync

The platform notification on the order trade execution in the external system.

C++
    
    
    MTAPIRES  IMTGatewayAPI::DealerExecuteAsync(
       IMTExecution*  execution      // Trade execution object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.DealerExecuteAsync(
       CIMTExecution  execution      // Trade execution object
       )

### Parameters

**execution**  
[in]Trade execution object.

### Return Value

If the command is successfully sent to the execution queue, the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code is returned. Otherwise, an error has occurred, which corresponds to the response code.

### Note

During the execution of this method the operation is carried out in the trading platform that corresponds to the executed one in the external environment.

### Example of partial Stop Loss execution and cancellation of activation for the remaining volume
    
    
    //+------------------------------------------------------------------+
    //| Partial position closing upon Stop Loss activation & cancellation|
    //| of StopLoss activation for remaining volume. Position with the |
    //| remaining volume stays in the platform till next SL activation   |
    //+------------------------------------------------------------------+
    void CExchange::AnswerExSLPartialFilled(const IMTRequest *request)
      { 
       MTAPISTR str              ={0};
       UINT64   volume           =request->Volume();  // Volume in the request to close by SL
       UINT64   filled_ex_volume =0;                  // Volume confirmed by the exchange
       UINT64   remaind_ex_volume=0;                  // volume which remained unfilled
       UINT64   delta            =5000;               // suppose the exchange always fills 0.5 lot less, 1 lot = 10000 units
       //---
       if(request->Volume()<=5000)
         {
          ExtLogger.Out(MTLogErr,L"Request volume =%I64u, exchange fill full volume",volume);
          filled_ex_volume=volume;
          remaind_ex_volume=0;
         }
       else
         {
          filled_ex_volume=volume - delta;
          remaind_ex_volume=delta;
          ExtLogger.Out(MTLogErr,L"Request volume =%I64u, exchange filled volume =%I64u, remained volume =%I64u,",volume,filled_ex_volume,remaind_ex_volume);
         }
       //---
       if((m_execution=m_api_gateway->DealerExecutionCreate())==NULL)
         {
          ExtLogger.Out(MTLogErr,L"failed to create execution interface");
          return;
         }
       //--- Process the executed part
       m_execution->Clear();
       m_execution->Order(request->ResultOrder());
       m_execution->Symbol(request->Symbol());
       m_execution->DealAction(request->Type());
       m_execution->DealVolume(filled_ex_volume);
       m_execution->DealVolumeRemaind(remaind_ex_volume);  // Set the remaining (unfilled) volume
       m_execution->DealPrice(request->PriceOrder());
       m_execution->Action(IMTExecution::TE_ORDER_FILL);
       //---
       if((m_api_gateway->DealerExecuteAsync(m_execution))!=MT_RET_OK)
         {
          ExtLogger.Out(MTLogErr,L"Send DealerExecuteAsync for request failed. Answer: %s",m_execution->Print(str));
         }
       else
         {
          ExtLogger.Out(MTLogErr,L"Answer: %s",m_execution->Print(str));
         }
       //--- Reset activation of the remaining volume for re-processing
       m_execution->Action(IMTExecution::TE_ORDER_CANCEL);
       //---
       if((m_api_gateway->DealerExecuteAsync(m_execution))!=MT_RET_OK)
         {
          ExtLogger.Out(MTLogErr,L"Send DealerExecuteAsync for OrderActivationMode failed. Answer: %s",m_execution->Print(str));
         }
       else
         {
          ExtLogger.Out(MTLogErr,L"Answer for OrderActivationMode: %s",m_execution->Print(str));
         }
       //---
       m_execution->Release();
    }

### Example of partial pending order execution and cancellation of activation for the remaining volume
    
    
    //+------------------------------------------------------------------+
    //| Partial execution of a pending order upon activation and         |
    //| canceling activation for remaining volume. Order with remaining |
    //| volume stays in the platform till next activation    |
    //+------------------------------------------------------------------+
    void CExchange::AnswerExPendingPartialFilled(const IMTRequest *request)
      {
       MTAPISTR    str              ={0};
       UINT        request_type;
       UINT64      volume           =request->Volume(); // Volume in the pending order request
       UINT64      filled_ex_volume =0;                 // Volume confirmed by the exchange
       UINT64      remaind_ex_volume=0;                 // volume which remained unfilled
       UINT64      delta            =5000;              // suppose the exchange always fills 0.5 lot less, 1 lot = 10000 units
       //---
       if(request->Volume()<=5000)
         {
          ExtLogger.Out(MTLogErr,L"Request volume =%I64u, exchange fill full volume",volume);
          filled_ex_volume=volume;
          remaind_ex_volume=0;
         }
       else
         {
          filled_ex_volume=volume - delta;
          remaind_ex_volume=delta;
          ExtLogger.Out(MTLogErr,L"Request volume =%I64u, exchange filled volume =%I64u, remaind volume =%I64u,",volume,filled_ex_volume,remaind_ex_volume);
         }
       //--- Change the pending order type to Market
       if(request->Type()==IMTOrder::OP_BUY_LIMIT || request->Type()==IMTOrder::OP_BUY_STOP)
         {
          request_type=IMTOrder::OP_BUY;
         }
       //---
       if(request->Type()==IMTOrder::OP_SELL_LIMIT || request->Type()==IMTOrder::OP_SELL_STOP)
         {
          request_type=IMTOrder::OP_SELL;
         }
       //---
       if((m_execution=m_api_gateway->DealerExecutionCreate())==NULL)
         {
          ExtLogger.Out(MTLogErr,L"failed to create execution interface");
          return;
         }
       //--- Process the executed part
       m_execution->Clear();
       m_execution->Order(request->ResultOrder());
       m_execution->Symbol(request->Symbol());
       m_execution->DealAction(request_type);
       m_execution->DealVolume(filled_ex_volume);
       m_execution->DealVolumeRemaind(remaind_ex_volume);  // Set the remaining (unfilled) volume
       m_execution->DealPrice(request->PriceOrder());
       m_execution->Action(IMTExecution::TE_ORDER_FILL);
       //---
       if((m_api_gateway->DealerExecuteAsync(m_execution))!=MT_RET_OK)
         {
          ExtLogger.Out(MTLogErr,L"Send DealerExecuteAsync for request failed. Answer: %s",m_execution->Print(str));
         }
       else
         {
          ExtLogger.Out(MTLogErr,L"Answer: %s",m_execution->Print(str));
         }
       //--- Reset activation of the remaining volume for re-processing
       m_execution->Action(IMTExecution::TE_ORDER_MODIFY);
       m_execution->OrderActivationMode(IMTOrder::ACTIVATION_NONE);
       //---
         if((m_api_gateway->DealerExecuteAsync(m_execution))!=MT_RET_OK)
           {
            ExtLogger.Out(MTLogErr,L"Send DealerExecuteAsync for OrderActivationMode failed. Answer: %s",m_execution->Print(str));
           }
         else
           {
            ExtLogger.Out(MTLogErr,L"Answer for OrderActivationMode: %s",m_execution->Print(str));
           }
         //---
         m_execution->Release();
    }

```

---

<a id='main-interface-processing-trade-requests-dealerexecutioncreate-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerExecutionCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerExecutionCreate

[Previous](DealerConfirmCreate.md) | [Next](DealerStart.md)

# IMTGatewayAPI::DealerExecutionCreate

Create trade execution method of this object.

C++
    
    
    IMTExecution*  IMTGatewayAPI::DealerExecutionCreate()

.NET
    
    
    CIMTExecution  CIMTGatewayAPI.DealerExecutionCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTExecution](../../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTExecution.md) interface. In case of failure, it returns NULL.

### Note

It returns a pointer to the created object that implements the [IMTExecution::Release](../../../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-Release.md) method of this project.

```

---

<a id='main-interface-processing-trade-requests-dealergetasync-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerGetAsync.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerGetAsync

[Previous](DealerStop.md) | [Next](DealerLockAsync.md)

# IMTGatewayAPI::DealerGetAsync

Capture the most early (old) request from the requests queue.

C++
    
    
    MTAPIRES  IMTGatewayAPI::DealerGetAsync()

.NET
    
    
    MTRetCode  CIMTGatewayAPI.DealerGetAsync()

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Request object captured as a result of this method calling is returned in the [IMTGatewaySink::OnDealerLock](../../Event-Interface/OnDealerLock.md) method.

```

---

<a id='main-interface-processing-trade-requests-dealerlockasync-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerLockAsync.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerLockAsync

[Previous](DealerGetAsync.md) | [Next](DealerAnswerAsync.md)

# IMTGatewayAPI::DealerLockAsync

Capture a request from the requests queue by ID.

C++
    
    
    MTAPIRES  IMTGatewayAPI::DealerLockAsync(
       const UINT  id      // Request ID
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.DealerLockAsync(
       uint  id           // Request ID
       )

### Parameters

**id**  
[in] ID of the request that is to be captured. TheIMTRequest::IDvalue is used as the identifier..

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code. Code MT_RET_OK_NONE means that the request is no longer available on the trade server. For example, it could have been captured by another dealer or application.

### Note

Request object captured as a result of this method calling is returned in the [IMTGatewaySink::OnDealerLock](../../Event-Interface/OnDealerLock.md) method.

```

---

<a id='main-interface-processing-trade-requests-dealerstart-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerStart.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerStart

[Previous](DealerExecutionCreate.md) | [Next](DealerStop.md)

# IMTGatewayAPI::DealerStart

Gateway connection to the trading platform as a dealer.

C++
    
    
    MTAPIRES  IMTGatewayAPI::DealerStart(
       const UINT  flags      // Connection flags
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.DealerStart(
       uint        flags      // Connection flags
       )

### Parameters

**flags**  
[in] The flags describing additional options for connection as a dealer. To pass the flags, theIMTGatewayAPI::EnDealerRequestFlagsenumeration is used.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

After this method execution the trade requests queue will be downloaded to the application and [trading requests events](../../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequestSink.md) will start coming (IMTRequestSink::OnRequestAdd, IMTRequestSink::OnRequestUpdate and IMTRequestSink::OnRequestDelete).

```

---

<a id='main-interface-processing-trade-requests-dealerstop-md'></a>
### 195. `Main-Interface/Processing-Trade-Requests/DealerStop.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Processing Trade Requests](../Processing-Trade-Requests.md) / DealerStop

[Previous](DealerStart.md) | [Next](DealerGetAsync.md)

# IMTGatewayAPI::DealerStop

[DealerStart](DealerStart.md) inverse method. After its successful execution the gateway will stop fulfilling the dealer functions.

C++
    
    
    MTAPIRES  IMTGatewayAPI::DealerStop()

.NET
    
    
    MTRetCode  CIMTGatewayAPI.DealerStop()

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

```

---

<a id='main-interface-quote-and-news-feeds-sendbookdiffs-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds/SendBookDiffs.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Quote and News Feeds](../Quote-and-News-Feeds.md) / SendBookDiffs

[Previous](SendTicks.md) | [Next](SendBooks.md)

# IMTGatewayAPI::SendBookDiffs

Send the Depth of Market changes.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SendBookDiffs(
       MTBookDiff*  bookdiffs,          // Depth of Market changes array
       const UINT   bookdiffs_total     // Number of the elements in the array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendBookDiffs(
       MTBook[]     bookdiffs           // Depth of Market changes array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendBookDiff(
       MTBook       bookdiffs           // A single change of the depth of market
       )

### Parameters

***bookdiffs**  
[in] A pointer to the array of the Depth of Market changes described by theMTBookDiffstructure.

**bookdiffs_total**  
[in] Number of the elements in the bookdiffs array.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred which corresponds to the response code.

### Note

This method sends the filled [MTBookDiff](../../../Structures/MTBookMTBookDiff.md) structures array to the trading platform.

## Filling MTBookDiff Structure

Each element of the aggregated depth of market is unique in type and price. The [MTBookDiff](../../../Structures/MTBookMTBookDiff.md) structure contains information about volume changes for a given type and price in the form of an array of MTBookItem [MTBookItem](../../../Structures/MTBookItem.md) elements. One MTBookDiff structure contains changes only for one instrument, described in the 'symbol' value of the structure.

Depth of Market change element types are listed below together with the actions of a history server when getting the elements of a specified type for the aggregative Depth of Market generation:

  * ItemReset — a history server will clean up the aggregative Depth of Market by the specified symbol when getting the element with such a type.
  * ItemSell, ItemBuy — a history server will look for the aggregative Depth of Market element by its type and price specified in MTBookItem when getting the [MTBookItem](../../../Structures/MTBookItem.md) structure with such a type. If the element is not found, then a new element (of MTBookItem type and price) is added to the aggregated depth of market. If the element is found in the aggregated depth of market, then element volume changes by the volume value, specified in the MTBookItem structure. In case a zero volume is indicated in the MTBookItem structure, the element found in the aggregative Depth of Market will be deleted.



  * The volume of element change in the aggregated depth of market, described in MTBookItem, can be both positive and negative.
  * The trading platform analyzes the items elements sent in the MTBookDiff structure strictly from the beginning to the end, consequently applying changes to the market depth.


  * All the symbol prices delivered into the platform are rounded in accordance with the [IMTConSymbol::Digits](../../../Configuration-Interfaces/Symbols/IMTConSymbol/Digits.md) parameter of the symbol. When broadcasting prices with higher accuracy, different levels can be combined into one rounded level. To avoid collisions, set the precision of the symbols in accordance with the precision of transmitted data.

  
---  
  
### Example

Let's analyze an example of how the difference between the Depths of Market at different time points is calculated:

Time point 1 | Time point 2 | Comparison result | Comment  
---|---|---|---  
Type | Price | Size | Type | Price | Size | Type | Price | Size  
Sell | 1.32464 | 5 | Sell | 1.32464 | 5 | Sell | 1.32463 | -3 | Bid volume with the price 1.32463 decreased by 3 lots.  
Sell | 1.32463 | 6 | Sell | 1.32463 | 3 | Buy | 1.32461 | 0 | Bid with the price 1.32461 disappeared from the Depth of Market.  
Buy | 1.32461 | 3 | Buy | 1.32460 | 4  | Buy | 1.32459 | 0 | Bid with the price 1.32459 disappeared from the Depth of Market.  
Buy | 1.32459 | 1 |  |  |  | Buy | 1.32460 | 4  | Bid with the price 1.32460 and the volume of 4 lots appeared in the Depth of Market.

```

---

<a id='main-interface-quote-and-news-feeds-sendbooks-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds/SendBooks.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Quote and News Feeds](../Quote-and-News-Feeds.md) / SendBooks

[Previous](SendBookDiffs.md) | [Next](SendNews.md)

# IMTGatewayAPI::SendBooks

Send the entire state of the Depth of Market.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SendBooks(
       MTBook*     books,           // Depth of Market array
       const UINT  books_total      // Number of the elements in the array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendBooks(
       MTBook[]    books            // Depth of Market array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendBooks(
       MTBook      books            // Single description of the depth of market
       )

### Parameters

**books**  
[in] A pointer to the array of the Depth of Market described by theMTBookstructure.

**books_total**  
[in] Number of the elements in the bookdiffs array.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

This method sends the filled [MTBook](../../../Structures/MTBookMTBookDiff.md) structures array to the trading platform.

All Market Depth items in one direction (buy or sell) must have different prices. If the source data contains several levels with the same price, you should aggregate them into one level with the total volume before sending them to the platform.

```

---

<a id='main-interface-quote-and-news-feeds-sendeconomicevents-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds/SendEconomicEvents.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Quote and News Feeds](../Quote-and-News-Feeds.md) / SendEconomicEvents

[Previous](SendNews.md) | [Next](../History-Data.md)

# IMTGatewayAPI::SendEconomicEvents

Sending economic calendar events.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SendEconomicEvents(
       MTEconomicEvent*  events,       // An array of economic news
       const UINT        events_total  // The number of elements in the array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendEconomicEvents(
       MTEconomicEvent[] events        // An array of economic news
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendEconomicEvent(
       MTEconomicEvent   events        // A single description of economic news
       )

### Parameters

**events**  
[in] A pointer to the array of news of the economic calendar described by theMTEconomicEventstructure.

**events_total**  
[in] The number of elements in the events array.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

The method is obsolete. It always returns [MT_RET_OK](../../../Return-Codes/Successful-completion.md) but does not perform any action.

  * datetime
  * name
  * currency
  * period



```

---

<a id='main-interface-quote-and-news-feeds-sendnews-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds/SendNews.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Quote and News Feeds](../Quote-and-News-Feeds.md) / SendNews

[Previous](SendBooks.md) | [Next](SendEconomicEvents.md)

# IMTGatewayAPI::SendNews

Passing the news.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SendNews(
       MTNews*     news,           // News array
       const UINT  news_total      // Number of the elements in the array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendNews(
       MTNews[]    news            // News array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendNews(
       MTNews      news            // A single description of news
       )

### Parameters

**news**  
[in] A pointer to the news array described by theMTNewsstructure.

**news_total**  
[in] Number of the elements in the news array.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

This method sends the filled [MTNews](../../../Structures/MTNews.md) structures array to the trading platform. After the news are sent, a programmer has to manually free the memory used for the news bodies (*body parameter in the MTNews structure).

```

---

<a id='main-interface-quote-and-news-feeds-sendtickstats-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds/SendTickStats.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Quote and News Feeds](../Quote-and-News-Feeds.md) / SendTickStats

[Previous](../Quote-and-News-Feeds.md) | [Next](SendTicks.md)

# IMTGatewayAPI::SendTickStats

Sending statistical information about a financial instrument.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SendTickStats(
       MTTickStat*  stats,           // Statistical data array
       const UINT   stats_total      // Number of the elements in the array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendTickStats(
       MTTickStat[] stats           // Statistical data array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendTickStat(
       MTTickStat   stats           // A single description of statistical data
       )

### Parameters

**stats**  
[in] A pointer to the statistical data array described by theMTTickStatstructure.

**stats_total**  
[in] Number of the elements in the stats array.

### Return Value

An indication of a successful execution is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

This method sends the filled [MTTickStat](../../../Structures/MTTickStat.md) structures array to the trading platform.

  * bid_high
  * bid_low
  * ask_high
  * ask_low


  * last_high
  * last_low
  * vol_high, vol_high_ext
  * vol_low, vol_low_ext



```

---

<a id='main-interface-quote-and-news-feeds-sendticks-md'></a>
### 195. `Main-Interface/Quote-and-News-Feeds/SendTicks.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Quote and News Feeds](../Quote-and-News-Feeds.md) / SendTicks

[Previous](SendTickStats.md) | [Next](SendBookDiffs.md)

# IMTGatewayAPI::SendTicks

Sending current prices.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SendTicks(
       MTTick*     ticks,          // Prices array
       const UINT  ticks_total     // Number of the elements in the array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendTicks(
       MTTick[]    ticks           // Prices array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SendTick(
       MTTick      ticks           // A single description of prices
       )

### Parameters

***ticks**  
[in] A pointer to the array of prices described by theMTTickstructure.

**ticks_total**  
[in] Number of the elements in the ticks array.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

This method sends the filled [MTTick](../../../Structures/MTTick.md) structures array to the trading platform.

```

---

<a id='main-interface-server-connections-md'></a>
### 195. `Main-Interface/Server/Connections.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Server](../Server.md) / Connections

[Previous](Port.md) | [Next](../External-Connection-State.md)

# IMTGatewayAPI::ServerConnections

Get the number of the client connections to the Gateway API server port.

C++
    
    
    UINT  IMTGatewayAPI::ServerConnections()

.NET
    
    
    uint  CIMTGatewayAPI.ServerConnections()

### Return Value

The number of the client connections to the Gateway API server port.

```

---

<a id='main-interface-server-ip-md'></a>
### 195. `Main-Interface/Server/IP.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Server](../Server.md) / IP

[Previous](Stop.md) | [Next](Port.md)

# IMTGatewayAPI::ServerIP

Get the IP address on which the Gateway API server port is running.

C++
    
    
    MTAPIRES  IMTGatewayAPI::ServerIP(
       MTAPISTR&  ip      // IP address
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.ServerIP(
       out string ip      // IP address
       )

### Parameters

**ip**  
[out] IP address on which the server port is running. In case several addresses have been specified viaIMTGatewayAPI::Startmethod, ServerIP method will return them in the same format - separated with a comma. For example, address1:port1,address2:port2.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

The IP address on which the Gateway API server port is running is determined by the [IMTGatewayAPI::Start](Start.md) method.

```

---

<a id='main-interface-server-port-md'></a>
### 195. `Main-Interface/Server/Port.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Server](../Server.md) / Port

[Previous](IP.md) | [Next](Connections.md)

# IMTGatewayAPI::ServerPort

Get the number of the port launched for the connection to Gateway API.

C++
    
    
    UINT  IMTGatewayAPI::ServerPort()

.NET
    
    
    uint  CIMTGatewayAPI.ServerPort()

### Return Value

Server port number. In case several addresses (for example: address1:port1,address2:port2) have been specified via [IMTGatewayAPI::Start](Start.md) method, this method will return the port of the first address (port1).

```

---

<a id='main-interface-server-start-md'></a>
### 195. `Main-Interface/Server/Start.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Server](../Server.md) / Start

[Previous](../Server.md) | [Next](Stop.md)

# IMTGatewayAPI::Start

Gateway API server port launch.

C++
    
    
    MTAPIRES  IMTGatewayAPI::Start(
       IMTGatewaySink  *sink,            // IMTGatewaySink interface object
       LPCWSTR         address=NULL      // Address
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.Start(
       CIMTGatewaySink sink,             // CIMTGatewaySink interface object
       string[]        address=NULL      // Address
       )

### Parameters

***sink**  
[in]IMTGatewaySinkinterface object for notifications on the platform and Gateway API events.

**address=NULL**  
[in] Address at which the client connections will be accepted. Defined as address:port. Several addresses separated with a comma can be specified here. For example, address1:port1,address2:port2. In case parameter value is not defined, default value is used. Address specified as the command line parameter during the launch of the executed gateway/data feed file is used as the default address. This address is passed in the argc and argv parameters of theCMTGatewayAPIFactory::Createmethod. In case the address is not specified neither in the IMTGatewayAPI::Start method, nor in the command line, the server port will not be launched.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

This method is called by the server during the gateway/data feed launch.

```

---

<a id='main-interface-server-stop-md'></a>
### 195. `Main-Interface/Server/Stop.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Server](../Server.md) / Stop

[Previous](Start.md) | [Next](IP.md)

# IMTGatewayAPI::Stop

Gateway API server port stop.

C++
    
    
    MTAPIRES  IMTGatewayAPI::Stop()

.NET
    
    
    MTRetCode CIMTGatewayAPI.Stop()

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

After [IMTGatewayAPI::Start](Start.md) call, the object which implements the [IMTGatewaySink](../../Event-Interface.md) interface is considered subscribed to notifications from the Gateway API. Such an object can only be deleted after calling IMTGatewayAPI::Stop. 

```

---

<a id='main-interface-synchronizing-trading-data-gatewayaccountanswer-md'></a>
### 195. `Main-Interface/Synchronizing-Trading-Data/GatewayAccountAnswer.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Synchronizing Trading Data](../Synchronizing-Trading-Data.md) / GatewayAccountAnswer

[Previous](../Synchronizing-Trading-Data.md) | [Next](GatewayAccountRequest.md)

# IMTGatewayAPI::GatewayAccountAnswer

The method is used to match client's MetaTrader 5 trading data (current pending orders, positions and balance) with an external trading system. After calling [IMTGatewaySink:HookGatewayAccountRequest](../../Event-Interface/HookGatewayAccountRequest.md) hook, a developer can transfer the state of positions, orders and client balance to MetaTrader 5 platform using this method. As a result of executing the method, the current pending orders, positions and client balance will match the passed data.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewayAccountAnswer(
       const MTAPIRES          result,           // Result
       const INT64             accounts_time,    // State fixing time
       const IMTUser*          user             // An object of a client record
       const IMTAccount*       account          // An object of a trading account
       const IMTOrderArray*    orders           // Array of orders
       const IMTPositionArray* positions        // Positions array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewayAccountAnswer(
       MTRetCode               result,           // Result
       long                    accounts_time,    // State fixing time
       CIMTUser                user              // An object of a client record
       CIMTAccount             account           // An object of a trading account
       CIMTOrderArray          orders            // Array of orders
       CIMTPositionArray       positions         // Positions array
       )

### Parameters

**result**  
[in] Code of the result of handling the client data request. MT_RET_OK response code is used if data has been successfully received. Otherwise, the appropriateerror codeis to be returned.

**accounts_time**  
[in] Time period, during which passed client trading status is actual. The date is specified in seconds since January 1, 1970.

**user**  
[in]An object of the client record.Loginfield is used in IMTUser object for identifying a user, for whom data synchronization is performed. The client external system's account number corresponding to the gateway can also be used for identification. Account in an external system can be defined usingIMTUser::ExternalAccountAddmethod.

**account**  
[in]Trading account object. OnlyBalancefield is used in IMTAccount object for passing the actual balance value.

**orders**  
[in]An object of the array of ordersplaced for the specified account. To avoid order synchronization, pass the NULL value.

**positions**  
[in]An object of the array of positionsplaced for the specified account. For a correct operation, the following fields ofIMTPositionobjects inside the array must be filled:

  * Symbol
  * Volume
  * ContractSize
  * Action
  * PriceOpen



### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

Correcting operations are created as a result of trading data synchronization. These operations are displayed in the client's trading history.

  * Balance: identification is based on the number of the client account in the external trading system, which corresponds to this gateway (it is set via [IMTUser::ExternalAccountAdd](../../../Database-Interfaces/Users/IMTUser/ExternalAccountAdd.md)). If the passed balance (the 'account' parameter) and the client's balance on the trade server do not match, a corrective balance deal is formed on the trade server. If the client's balance on the trade server is zero (when balance should be added), the deal type will be [IMTDeal::DEAL_BALANCE (#endealaction)](../../../Database-Interfaces/Trade/Deals/IMTDeal/Enumerations.md#endealaction). Otherwise the deal type is [IMTDeal::DEAL_CORRECTION (#endealaction)](../../../Database-Interfaces/Trade/Deals/IMTDeal/Enumerations.md#endealaction).
  * Orders: when the method is called, the equality of the list of passed orders (the 'orders' parameter) and the client's list of orders on the trade server is checked. The following details are checked: the order ID in an external trading system ([IMTOrder::ExternalID](../../../Database-Interfaces/Trade/Orders/IMTOrder/ExternalID.md)), the trading symbol ([IMTOrder::Symbol](../../../Database-Interfaces/Trade/Orders/IMTOrder/Symbol.md)), the order type ([IMTOrder::Type](../../../Database-Interfaces/Trade/Orders/IMTOrder/Type.md)), the current volume ([IMTOrder::VolumeCurrent](../../../Database-Interfaces/Trade/Orders/IMTOrder/VolumeCurrent.md)) and the order price ([IMTOrder::PriceOrder](../../../Database-Interfaces/Trade/Orders/IMTOrder/PriceOrder.md)). If the lists are equal, synchronization of orders is considered completed. If the lists do not match, orders existing on the trade server are canceled and an appropriate log is added to the server journal. After that new orders passed by the gateway are placed. The server tries to preserve the SL\TP values, if the external ID, trading symbol, direction and price of the order have not changed.
  * Positions: when the method is called, the equality of the list of passed positions (the 'positions' parameter) and the client's list of positions on the trade server is checked. The following details are checked: the position ID in an external trading system ([IMTPosition::ExternalID](../../../Database-Interfaces/Trade/Positions/IMTPosition/ExternalID.md)), the trading symbol ([IMTPosition::Symbol](../../../Database-Interfaces/Trade/Positions/IMTPosition/Symbol.md)), position direction ([IMTPosition::Action](../../../Database-Interfaces/Trade/Positions/IMTPosition/Action.md)), volume ([IMTPosition::VolumeCurrent](../../../Database-Interfaces/Trade/Positions/IMTPosition/Volume.md)), open price ([IMTPosition::PriceOpen](../../../Database-Interfaces/Trade/Positions/IMTPosition/PriceOpen.md)) and contract size ([IMTPosition::ContractSize](../../../Database-Interfaces/Trade/Positions/IMTPosition/ContractSize.md)). If the lists are equal, synchronization of positions is considered completed. If the lists do not match:


  * Positions, which exist on the trade server but are not found in the passed list, are closed with zero profit.
  * Positions, which do not exist on the trade server but are included in the passed list, are added to the client's account.
  * Positions with matching trading symbols existing in both lists are compared. If the direction, open price or contract size of a position has changed, the position on the trade server is closed and a new one received via the gateway is opened. If only the volume of a position has changed, the position on the trade server is corrected via an appropriate deal.



```

---

<a id='main-interface-synchronizing-trading-data-gatewayaccountrequest-md'></a>
### 195. `Main-Interface/Synchronizing-Trading-Data/GatewayAccountRequest.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Synchronizing Trading Data](../Synchronizing-Trading-Data.md) / GatewayAccountRequest

[Previous](GatewayAccountAnswer.md) | [Next](GatewayAccountSet.md)

# IMTGatewayAPI::GatewayAccountRequest

This method allows Gateway API to request information about a user state in MetaTrader 5 platform. Request result and the requested information are passed to [IMTGatewayAPI::OnGatewayAccountAnswer](../../Event-Interface/OnGatewayAccountAnswer.md) handler.

C++
    
    
    MTAPIRES  IMTGatewaySink::GatewayAccountRequest(
       const INT64    request_id,  // Request ID
       const IMTUser* user         // Login
       )

.NET
    
    
    MTRetCode  CIMTGatewaySink.GatewayAccountRequest(
       long           request_id,  // Request ID
       CIMTUser       user         // Login
       )

### Parameters

**request_id**  
[in] Arbitrary request ID. It is used for binding the requests executed by this method and the answers received viaIMTGatewayAPI::OnGatewayAccountAnswer.

**user**  
[in]An object of the client record.Loginfield is used in IMTUser object for identifying a user, for whom data request is performed. The client external system's account number corresponding to the gateway can also be used for identification. Account in an external system can be defined usingIMTUser::ExternalAccountAddmethod.

### Return Value

An indication of a successful placing of a request to the processing queue is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### 

```

---

<a id='main-interface-synchronizing-trading-data-gatewayaccountset-md'></a>
### 195. `Main-Interface/Synchronizing-Trading-Data/GatewayAccountSet.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Synchronizing Trading Data](../Synchronizing-Trading-Data.md) / GatewayAccountSet

[Previous](GatewayAccountRequest.md) | [Next](../Mail-Database.md)

# IMTGatewayAPI::GatewayAccountSet

The method is used to match client's MetaTrader 5 trading data (current pending orders, positions and balance) with an external trading system. Using this method, a developer can transfer the state of positions, orders and client balance to MetaTrader 5 platform. As a result of executing the method, the current pending orders, positions and client balance will match the passed data.

C++
    
    
    MTAPIRES  IMTGatewayAPI::GatewayAccountSet(
       const INT64             request_id        // Request ID
       const IMTUser*          user              // An object of a client record
       const IMTAccount*       account           // An object of a trading account
       const IMTOrderArray*    orders            // Array of orders
       const IMTPositionArray* positions         // Positions array
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.GatewayAccountSet(
       long                    request_id        // Request ID
       CIMTUser                user              // An object of a client record
       CIMTAccount             account           // An object of a trading account
       CIMTOrderArray          orders            // Positions array
       CIMTPositionArray       positions         // Positions array
       )

### Parameters

**request_id**  
[in] Arbitrary request ID. It is used for binding the requests executed by this method and the answers received viaIMTGatewayAPI::OnGatewayAccountSet.

**user**  
[in]An object of the client record. The client external system's account number corresponding to the gateway is used for identification of the user, for whom data synchronization is performed. Account in an external system can be defined usingIMTUser::ExternalAccountAddmethod.

**account**  
[in]Trading account object. OnlyBalancefield is used in IMTAccount object for passing the actual balance value.

**orders**  
[in]An object of the array of ordersplaced for the specified account. To avoid order synchronization, pass the NULL value.

**positions**  
[in]An object of the array of positionsplaced for the specified account. For a correct operation, the following fields ofIMTPositionobjects inside the array must be filled:

  * Symbol
  * Volume
  * ContractSize
  * Action
  * PriceOpen



### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

Execution result, as well as the final status of a client entry are passed to [IMTGatewaySink::OnGatewayAccountSet](../../Event-Interface/OnGatewayAccountSet.md) handler.

If this condition is not met for any of the passed orders, synchronization stops with an error.

After that the system copies the orders which are not available in the current list (which were not found by ticket or ID).

  * [IMTOrder::Symbol](../../../Database-Interfaces/Trade/Orders/IMTOrder/Symbol.md)
  * [IMTOrder::VolumeInitial](../../../Database-Interfaces/Trade/Orders/IMTOrder/VolumeInitial.md)
  * [IMTOrder::VolumeCurrent](../../../Database-Interfaces/Trade/Orders/IMTOrder/VolumeCurrent.md) (must be less than or equal to [IMTOrder::VolumeInitial](../../../Database-Interfaces/Trade/Orders/IMTOrder/VolumeInitial.md))
  * [IMTOrder::PriceOrder](../../../Database-Interfaces/Trade/Orders/IMTOrder/PriceOrder.md) (must be non-zero)
  * [IMTOrder::State](../../../Database-Interfaces/Trade/Orders/IMTOrder/State.md) (must be ORDER_STATE_STARTED, ORDER_STATE_PLACED, ORDER_STATE_PARTIAL or ORDER_STATE_REQUEST_*)


  * [IMTOrder::Order](../../../Database-Interfaces/Trade/Orders/IMTOrder/Order.md)
  * [IMTOrder::ExternalID](../../../Database-Interfaces/Trade/Orders/IMTOrder/ExternalID.md)
  * [IMTOrder::Symbol](../../../Database-Interfaces/Trade/Orders/IMTOrder/Symbol.md)
  * [IMTOrder::Type](../../../Database-Interfaces/Trade/Orders/IMTOrder/Type.md)
  * [IMTOrder::VolumeCurrent](../../../Database-Interfaces/Trade/Orders/IMTOrder/VolumeCurrent.md)
  * [IMTOrder::PriceOrder](../../../Database-Interfaces/Trade/Orders/IMTOrder/PriceOrder.md)
  * [IMTOrder::State](../../../Database-Interfaces/Trade/Orders/IMTOrder/State.md) (if this field in the incoming order is different from ORDER_STATE_STARTED)


  * [IMTOrder::Order](../../../Database-Interfaces/Trade/Orders/IMTOrder/Order.md)
  * [IMTOrder::PriceTP](../../../Database-Interfaces/Trade/Orders/IMTOrder/PriceTP.md)
  * [IMTOrder::PriceSL](../../../Database-Interfaces/Trade/Orders/IMTOrder/PriceSL.md)
  * [IMTOrder::State](../../../Database-Interfaces/Trade/Orders/IMTOrder/State.md) (if this field in the incoming order is ORDER_STATE_STARTED)
  * [IMTOrder::ContractSize](../../../Database-Interfaces/Trade/Orders/IMTOrder/ContractSize.md)
  * [IMTOrder::Digits](../../../Database-Interfaces/Trade/Orders/IMTOrder/Digits.md)
  * [IMTOrder::DigitsCurrency](../../../Database-Interfaces/Trade/Orders/IMTOrder/DigitsCurrency.md)


  * Positions which exist on the trade server but are not found in the passed list, are closed with zero profit.
  * Positions which do not exist on the trade server but are included in the passed list, are added to the client's account.
  * Positions with matching trading symbols existing in both lists are compared. If the direction, open price or contract size of a position has changed, the position on the trade server is closed and a new one received via the gateway is opened. If only the volume of a position has changed, the position on the trade server is corrected via an appropriate deal.



```

---

<a id='main-interface-tick-data-tickhistoryadd-md'></a>
### 195. `Main-Interface/Tick-Data/TickHistoryAdd.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Tick Data](../Tick-Data.md) / TickHistoryAdd

[Previous](TickHistoryRequestRaw.md) | [Next](TickHistoryReplace.md)

# IMTGatewayAPI::TickHistoryAdd

Add tick data of a symbol.

C++
    
    
    MTAPIRES  IMTGatewayAPI::TickHistoryAdd(
       LPCWSTR             symbol,         // Symbol
       const MTTickRate*   ticks,          // Ticks to add
       const UINT          ticks_total     // Number of ticks to add
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.TickHistoryAdd(
       string              symbol,         // Symbol
       MTTickRate[]        ticks           // Ticks to add
       )

### Parameters

**symbol**  
[in] The symbol, for which you want to update tick data.

**ticks**  
[in] Array ofMTTickRatestructures, which describe the ticks being added.

**ticks_total**  
[in] The number of ticks to add.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

Unlike [IMTGatewayAPI::SendTicks](../Quote-and-News-Feeds/SendTicks.md), this method directly adds quotes to the price history rather than adding them to the price stream.

```

---

<a id='main-interface-tick-data-tickhistoryreplace-md'></a>
### 195. `Main-Interface/Tick-Data/TickHistoryReplace.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Tick Data](../Tick-Data.md) / TickHistoryReplace

[Previous](TickHistoryAdd.md) | [Next](../Users.md)

# IMTGatewayAPI::TickHistoryReplace

Completely replace tick data in the specified period by the transmitted data

C++
    
    
    MTAPIRES  IMTGatewayAPI::TickHistoryReplace(
       LPCWSTR             symbol,        // Symbol
       const INT64         from_msc,      // Beginning of the period
       const INT64         to_msc,        // End of the period
       const MTTickRate*  ticks,         // New ticks
       const UINT          ticks_total    // Number of new ticks
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.TickHistoryReplace(
       string              symbol,        // Symbol
       long                from_msc,      // Beginning of the period
       long                to_msc,        // End of period
       MTTickRate[]        ticks          // New ticks
       )

### Parameters

**symbol**  
[in] The symbol, for which you want to update tick data.

**from_msc**  
[in] The beginning date of the period for which you want to replace history data. The date is specified in milliseconds since 01.01.1970.

**to_msc**  
[in] The end date of the period for which you want to replace history data. The date is specified in milliseconds since 01.01.1970.

**ticks**  
[in] Array ofMTTickRatestructures, which describe the new ticks.

**ticks_total**  
[in] The number of passed ticks.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method completely replaces tick data in the specified time interval with the data passed in the 'ticks' parameter.

```

---

<a id='main-interface-tick-data-tickhistoryrequest-md'></a>
### 195. `Main-Interface/Tick-Data/TickHistoryRequest.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Tick Data](../Tick-Data.md) / TickHistoryRequest

[Previous](../Tick-Data.md) | [Next](TickHistoryRequestRaw.md)

# IMTGatewayAPI::TickHistoryRequest

Get quotes for a symbol in the specified time range.

C++
    
    
    MTAPIRES  IMTGatewayAPI::TickHistoryRequest(
       LPCWSTR        symbol,          // Symbol
       const INT64    from,            // Beginning date
       const INT64    to,              // End date
       MTTickRate*&   ticks,           // Link to an array of quote structures
       UINT&          ticks_total      // Number of quotes
       )

.NET
    
    
    MTTickRate[]  CIMTGatewayAPI.TickHistoryRequest(
       string         symbol,          // Symbol
       long           from,            // Beginning date
       long           to,              // End date
       out MTRetCode  res              // Response code
       )

### Parameters

**symbol**  
[in] The name of the symbol, for which you need to get quotes.

**from**  
[in] The start date for requesting quotes. The date is specified in seconds since 01.01.1970.

**to**  
[in] The end date for requesting quotes. The date is specified in seconds since 01.01.1970.

**ticks**  
[out] A reference to the array of structures which describe quotes (MTTickRate).

**ticks_total**  
[out] The total number of received quotes.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

After the use, the [MTTickRate](../../../Structures/MTTickRate.md) array of structures must be released using the [IMTGatewayAPI::Free](../Common-Functions/Free.md) method.

```

---

<a id='main-interface-tick-data-tickhistoryrequestraw-md'></a>
### 195. `Main-Interface/Tick-Data/TickHistoryRequestRaw.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Tick Data](../Tick-Data.md) / TickHistoryRequestRaw

[Previous](TickHistoryRequest.md) | [Next](TickHistoryAdd.md)

# IMTGatewayAPI::TickHistoryRequestRaw

Get the entire stream of quotes for a symbol (raw and processed prices in accordance with the configuration of the symbol) in the specified time range.

C++
    
    
    MTAPIRES  IMTGatewayAPI::TickHistoryRequestRaw(
       LPCWSTR        symbol,          // Symbol
       const INT64    from,            // Beginning date
       const INT64    to,              // End date
       MTTickRate*&   ticks,           // Link to an array of quote structures
       UINT&          ticks_total      // Number of quotes
       )

.NET
    
    
    MTTickRate[]  CIMTGatewayAPI.TickHistoryRequestRaw(
       string         symbol,          // Symbol
       long           from,            // Beginning date
       long           to,              // End date
       out MTRetCode  res              // Response code
       )

### Parameters

**symbol**  
[in] The name of the symbol, for which you need to get quotes.

**from**  
[in] The start date for requesting quotes. The date is specified in seconds since 01.01.1970.

**to**  
[in] The end date for requesting quotes. The date is specified in seconds since 01.01.1970.

**ticks**  
[out] A reference to the array of structures which describe quotes (MTTickRate).

**ticks_total**  
[out] The total number of received quotes.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

If the raw quote storing option ([IMTConSymbol::TickFlags](../../../Configuration-Interfaces/Symbols/IMTConSymbol/TickFlags.md)) is disabled in symbol settings, only the quote which were accepted by the server are received, i.e. the operation is similar to the [IMTAdminAPI::TickRequest](../../../Manager-API/Administrator-Interface/Tick-Data/TickRequest.md) method call.

After the use, the [MTTickRate](../../../Structures/MTTickRate.md) array of structures must be released using the [IMTGatewayAPI::Free](../Common-Functions/Free.md) method.

The method cannot be called from event handlers (any IMT*Sink class methods).

```

---

<a id='main-interface-trade-databases-ordercreate-md'></a>
### 195. `Main-Interface/Trade-Databases/OrderCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Databases](../Trade-Databases.md) / OrderCreate

[Previous](../Trade-Databases.md) | [Next](PositionCreate.md)

# IMTGatewayAPI::OrderCreate

Create an object of a trade order.

C++
    
    
    IMTOrder*  IMTGatewayAPI::OrderCreate()

.NET
    
    
    CIMTOrder  CIMTGatewayAPI.OrderCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTOrder](../../../Database-Interfaces/Trade/Orders/IMTOrder.md) interface. In case of failure, it returns NULL.

### Note

The created object must be deleted by calling the [IMTOrder::Release](../../../Database-Interfaces/Trade/Orders/IMTOrder/Release.md) method of this object.

```

---

<a id='main-interface-trade-databases-positioncreate-md'></a>
### 195. `Main-Interface/Trade-Databases/PositionCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Databases](../Trade-Databases.md) / PositionCreate

[Previous](OrderCreate.md) | [Next](../Trade-Requests.md)

# IMTGatewayAPI::PositionCreate

Create an object of a trade position.

C++
    
    
    IMTPosition*  IMTGatewayAPI::PositionCreate()

.NET
    
    
    CIMTPosition  CIMTGatewayAPI.PositionCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTPosition](../../../Database-Interfaces/Trade/Positions/IMTPosition.md) interface. In case of failure, it returns NULL.

### Note

The created object must be deleted by calling the [IMTPosition::Release](../../../Database-Interfaces/Trade/Positions/IMTPosition/Release.md) method of this object.

```

---

<a id='main-interface-trade-requests-requestarraycreate-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestArrayCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestArrayCreate

[Previous](RequestCreate.md) | [Next](RequestSubscribe.md)

# IMTGatewayAPI::RequestArrayCreate

Create an object of the array of trade requests.

C++
    
    
    IMTRequestArray*  IMTGatewayAPI::RequestArrayCreate()

.NET
    
    
    CIMTRequestArray  CIMTGatewayAPI.RequestArrayCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTRequestArray](../../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequestArray.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTRequestArray::Release](../../../Database-Interfaces/Trade/Trade-Requests/IMTRequestArray/Requests-Release.md) method of this object.

```

---

<a id='main-interface-trade-requests-requestcreate-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestCreate

[Previous](../Trade-Requests.md) | [Next](RequestArrayCreate.md)

# IMTGatewayAPI::RequestCreate

Create an object of a trade request.

C++
    
    
    IMTRequest*  IMTGatewayAPI::RequestCreate()

.NET
    
    
    CIMTRequest  CIMTGatewayAPI.RequestCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTRequest](../../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequest.md) interface. In case of failure, it returns NULL.

### Note

The created object must be destroyed by calling the [IMTRequest::Release](../../../Database-Interfaces/Trade/Trade-Requests/IMTRequest/Requests-Release.md) method of this object.

```

---

<a id='main-interface-trade-requests-requestget-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestGet.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestGet

[Previous](RequestNext.md) | [Next](RequestGetAll.md)

# IMTGatewayAPI::RequestGet

Get a trade request by ID.

C++
    
    
    MTAPIRES  IMTGatewayAPI::RequestGet(
       const UINT   id,          // Request ID
       IMTRequest*  request      // An object of a trade request
       IMTUser*     user         // An object of the client record
       IMTAccount*  account      // An object of a trading account
       IMTOrder*    order        // An order object
       IMTPosition* position     // Position object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.RequestGet(
       uint         id,          // Request ID
       CIMTRequest  request      // An object of a trade request
       CIMTUser     user         // An object of the client record
       CIMTAccount  account      // An object of a trading account
       CIMTOrder    order        // An order object
       CIMTPosition position     // Position object
       )

### Parameters

**id**  
[in] Trade request ID. TheIMTRequest::Idvalue is used as the identifier.

**request**  
[out] An object of a trade request. The request object must first be created using theIMTGatewayAPI::RequestCreatemethod.

**user**  
[out] An object of the client login. The user object must first be created using theIMTGatewayAPI::UserCreatemethod.

**account**  
[out] An object of a client trading account. The account object must first be created using theIMTGatewayAPI::UserCreateAccountmethod.

**order**  
[out] An object of a trade order. The order object must first be created using theIMTGatewayAPI::OrderCreatemethod.

**position**  
[out] A trade position object of a trade request. The position object must first be created using theIMTGatewayAPI::PositionCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

[IMTGatewayAPI::DealerStart](../Processing-Trade-Requests/DealerStart.md) must be preliminarily called for making this method work.

```

---

<a id='main-interface-trade-requests-requestgetall-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestGetAll.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestGetAll

[Previous](RequestGet.md) | [Next](../Gateway-Symbols.md)

# IMTGatewayAPI::RequestGetAll

Get all the trade requests in a queue.

C++
    
    
    MTAPIRES  IMTGatewayAPI::RequestGetAll(
       IMTRequestArray*  requests      // An object of the array of requests
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.RequestGetAll(
       CIMTRequestArray  requests      // An object of the array of requests
       )

### Parameters

**requests**  
[out] An object of the array of requests. The requests object must first be created using theIMTGatewaAPI::RequestArrayCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

This method copies the array of trade requests in a queue to the requests object. [IMTGatewayAPI::DealerStart](../Processing-Trade-Requests/DealerStart.md) must be preliminarily called for making the method work.

```

---

<a id='main-interface-trade-requests-requestnext-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestNext.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestNext

[Previous](RequestTotal.md) | [Next](RequestGet.md)

# IMTGatewayAPI::RequestNext

Get a trade request by a queue position.

C++
    
    
    MTAPIRES  IMTGatewayAPI::RequestNext(
       const UINT   pos,         // Trade request position
       IMTRequest*  request      // An object of a trade request
       IMTUser*     user         // An object of the client record
       IMTAccount*  account      // An object of a trading account
       IMTOrder*    order        // An order object
       IMTPosition* position     // Position object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.RequestNext(
       uint         pos,         // Trade request position
       CIMTRequest  request      // An object of a trade request
       CIMTUser     user         // An object of the client record
       CIMTAccount  account      // An object of a trading account
       CIMTOrder    order        // An order object
       CIMTPosition position     // Position object
       )

### Parameters

**pos**  
[in] Position of a trade request in a queue, starting with 0.

**request**  
[out] An object of a trade request. The request object must first be created using theIMTGatewayAPI::RequestCreatemethod.

**user**  
[out] An object of the client login. The user object must first be created using theIMTGatewayAPI::UserCreatemethod.

**account**  
[out] An object of a client trading account. The account object must first be created using theIMTGatewayAPI::UserCreateAccountmethod.

**order**  
[out] An object of a trade order. The order object must first be created using theIMTGatewayAPI::OrderCreatemethod.

**position**  
[out] A trade position object of a trade request. The position object must first be created using theIMTGatewayAPI::PositionCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

This method copies trade request data at the specified queue position to the request object. [IMTGatewayAPI::DealerStart](../Processing-Trade-Requests/DealerStart.md) must be preliminarily called for making the method work.

```

---

<a id='main-interface-trade-requests-requestsubscribe-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestSubscribe.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestSubscribe

[Previous](RequestArrayCreate.md) | [Next](RequestUnsubscribe.md)

# IMTGatewayAPI::RequestSubscribe

Subscribe to events associated with trade requests queue changes.

C++
    
    
    MTAPIRES  IMTGatewayAPI::RequestSubscribe(
       IMTRequestSink*  sink      // A pointer to the IMTRequestSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.RequestSubscribe(
       CIMTRequestSink  sink      // CIMTRequestSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTRequestSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred that corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same interface [IMTRequestSink](../../../Database-Interfaces/Trade/Trade-Requests/Requests-IMTRequestSink.md) cannot subscribe to an event twice - in this case the response code [MT_RET_ERR_DUPLICATE](../../../Return-Codes/Common-errors.md) is returned.

```

---

<a id='main-interface-trade-requests-requesttotal-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestTotal.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestTotal

[Previous](RequestUnsubscribe.md) | [Next](RequestNext.md)

# IMTGatewayAPI::RequestTotal

Get the total amount of trade requests in a requests queue.

C++
    
    
    UINT  IMTGatewayAPI::RequestTotal()

.NET
    
    
    uint  CIMTGatewayAPI.RequestTotal()

### Return Value

Total amount of trade requests in a requests queue.

### Note

[IMTGatewayAPI::DealerStart](../Processing-Trade-Requests/DealerStart.md) must be preliminarily called for making this method work.

```

---

<a id='main-interface-trade-requests-requestunsubscribe-md'></a>
### 195. `Main-Interface/Trade-Requests/RequestUnsubscribe.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Trade Requests](../Trade-Requests.md) / RequestUnsubscribe

[Previous](RequestSubscribe.md) | [Next](RequestTotal.md)

# IMTGatewayAPI::RequestUnsubscribe

Unsubscribe from events associated with requests queue changes.

C++
    
    
    MTAPIRES  IMTGatewayAPI::RequestUnsubscribe(
       IMTRequestSink*  sink      // A pointer to the IMTRequestSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.RequestUnsubscribe(
       CIMTRequestSink  sink      // CIMTRequestSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTRequestSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This is a pair method to [IMTGatewayAPI::RequestSubscribe](RequestSubscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../Return-Codes/Common-errors.md) error is returned.

```

---

<a id='main-interface-user-settings-settingsadd-md'></a>
### 195. `Main-Interface/User-Settings/SettingsAdd.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsAdd

[Previous](../User-Settings.md) | [Next](SettingsUpdate.md)

# IMTGatewayAPI::SettingsAdd

Add a setting.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsAdd(
       const  IMTConParam*  param      // Setting object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsAdd(
       CIMTConParam         param      // Setting object
       )

### Parameters

**param**  
[in]Setting object.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

A setting object must be created using the method [IMTGatewayAPI::FeederParamCreate](../Configuration-Databases/Data-Feeds/FeederParamCreate.md) or [IMTGatewayAPI::GatewayParamCreate](../Configuration-Databases/Gateways/GatewayParamCreate.md). Further, assign a name and a value to the param object using methods [IMTConParam::Name](../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Name.md) and [IMTConParamValue](../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Value.md) respectively.

```

---

<a id='main-interface-user-settings-settingsclear-md'></a>
### 195. `Main-Interface/User-Settings/SettingsClear.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsClear

[Previous](SettingsDelete.md) | [Next](SettingsTotal.md)

# IMTGatewayAPI::SettingsClear

Delete all settings.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsClear()

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsClear()

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This method deletes all settings and the settings.dat file.

```

---

<a id='main-interface-user-settings-settingsdelete-md'></a>
### 195. `Main-Interface/User-Settings/SettingsDelete.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsDelete

[Previous](SettingsUpdate.md) | [Next](SettingsClear.md)

# IMTGatewayAPI::SettingsDelete

Delete a setting by its position.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsDelete(
       const UINT    pos        // Setting position
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsDelete(
       uint          pos        // Setting position
       )

### Parameters

**pos**  
[in] The position of a setting in the settings.dat file, starting with 0.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

# IMTGatewayAPI::SettingsDelete

Delete a setting by its name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsDelete(
       LPCWSTR       name       // Setting name
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsDelete(
       string        name       // Setting name
       )

### Parameters

**name**  
[in] The name of the setting you want to delete.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method deletes the first found setting with the specified name.

```

---

<a id='main-interface-user-settings-settingsget-md'></a>
### 195. `Main-Interface/User-Settings/SettingsGet.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsGet

[Previous](SettingsNext.md) | [Next](../../Event-Interface.md)

# IMTGatewayAPI::SettingsGet

Get a setting by its name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsGet(
       LPCWSTR       name,      // Setting name
       IMTConParam*  param      // Setting object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsGet(
       string        name,      // Setting name
       CIMTConParam  param      // Setting object
       )

### Parameters

**name**  
[in] The name of the setting.

**param**  
[out]An object of the parameter setting. The param object must first be created using the methodIMTGatewayAPI::FeederParamCreateorIMTGatewayAPI::GatewayParamCreate.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method returns the first found setting with the specified name.

```

---

<a id='main-interface-user-settings-settingsnext-md'></a>
### 195. `Main-Interface/User-Settings/SettingsNext.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsNext

[Previous](SettingsTotal.md) | [Next](SettingsGet.md)

# IMTGatewayAPI::SettingsNext

Get a setting by its position.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsNext(
       const UINT    pos,       // Setting position
       IMTConParam*  param      // Setting object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsNext(
       uint          pos,       // Setting position
       CIMTConParam  param      // Setting object
       )

### Parameters

**pos**  
[in] The position of a setting in the settings.dat file, starting with 0.

**param**  
[out]An object of the setting. The param object must first be created using the methodIMTGatewayAPI::FeederParamCreateorIMTGatewayAPI::GatewayParamCreate.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

```

---

<a id='main-interface-user-settings-settingstotal-md'></a>
### 195. `Main-Interface/User-Settings/SettingsTotal.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsTotal

[Previous](SettingsClear.md) | [Next](SettingsNext.md)

# IMTGatewayAPI::SettingsTotal

Get the number of settings.

C++
    
    
    UINT  IMTGatewayAPI::SettingsTotal()

.NET
    
    
    uint  CIMTGatewayAPI.SettingsTotal()

### Return Value

Number of settings in the file settings.dat.

```

---

<a id='main-interface-user-settings-settingsupdate-md'></a>
### 195. `Main-Interface/User-Settings/SettingsUpdate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [User Settings](../User-Settings.md) / SettingsUpdate

[Previous](SettingsAdd.md) | [Next](SettingsDelete.md)

# IMTGatewayAPI::SettingsUpdate

Change a setting at the specified position.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsUpdate(
       const UINT          pos        // Setting position
       const IMTConParam*  param      // Setting object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsUpdate(
       uint                pos        // Setting position
       CIMTConParam        param      // Setting object
       )

### Parameters

**pos**  
[in] The position of a setting in the settings.dat file, starting with 0.

**param**  
[in]An object of a new setting.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

A setting object must be created using the method [IMTGatewayAPI::FeederParamCreate](../Configuration-Databases/Data-Feeds/FeederParamCreate.md) or [IMTGatewayAPI::GatewayParamCreate](../Configuration-Databases/Gateways/GatewayParamCreate.md). Further, assign a name and a value to the param object using methods [IMTConParam::Name](../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Name.md) and [IMTConParamValue](../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Value.md) respectively.

# IMTGatewayAPI::SettingsUpdate

Change a setting by its name.

C++
    
    
    MTAPIRES  IMTGatewayAPI::SettingsUpdate(
       const IMTConParam*  param      // Setting object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.SettingsUpdate(
       CIMTConParam        param      // Setting object
       )

### Parameters

**param**  
[in]An object of a new setting. The name of the setting to modify and the new value to assign to the setting are specified in the object.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

A setting object must be created using the method [IMTGatewayAPI::FeederParamCreate](../Configuration-Databases/Data-Feeds/FeederParamCreate.md) or [IMTGatewayAPI::GatewayParamCreate](../Configuration-Databases/Gateways/GatewayParamCreate.md). Further, assign a name and a value to the param object using methods [IMTConParam::Name](../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Name.md) and [IMTConParamValue](../../../Configuration-Interfaces/Additional-Parameters/IMTConParam/Value.md) respectively.

```

---

<a id='main-interface-users-usercreate-md'></a>
### 195. `Main-Interface/Users/UserCreate.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserCreate

[Previous](../Users.md) | [Next](UserCreateAccount.md)

# IMTGatewayAPI::UserCreate

Create an object of a client record.

C++
    
    
    IMTUser*  IMTGatewayAPI::UserCreate()

.NET
    
    
    CIMTUser  CIMTGatewayAPI.UserCreate()

### Return Value

It returns a pointer to the created object that implements the [IMTUser](../../../Database-Interfaces/Users/IMTUser.md) interface. In case of failure, it returns NULL.

### Note

The created object must be deleted by calling the [IMTUser::Release](../../../Database-Interfaces/Users/IMTUser/Release.md) method of this object.

```

---

<a id='main-interface-users-usercreateaccount-md'></a>
### 195. `Main-Interface/Users/UserCreateAccount.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserCreateAccount

[Previous](UserCreate.md) | [Next](UserSubscribe.md)

# IMTGatewayAPI::UserCreateAccount

Create an object of a client's trading account.

C++
    
    
    IMTAccount*  IMTGatewayAPI::UserCreateAccount()

.NET
    
    
    CIMTAccount  CIMTGatewayAPI.UserCreateAccount()

### Return Value

It returns a pointer to the created object that implements the [IMTAccount](../../../Database-Interfaces/Trade/Accounts/IMTAccount.md) interface. In case of failure, it returns NULL.

### Note

The created object must be deleted by calling the [IMTAccount::Release](../../../Database-Interfaces/Trade/Accounts/IMTAccount/Release.md) method of this object.

```

---

<a id='main-interface-users-userget-md'></a>
### 195. `Main-Interface/Users/UserGet.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserGet

[Previous](UserTotal.md) | [Next](UserGetByAccount.md)

# IMTGatewayAPI::UserGet

Get a client record by the login.

C++
    
    
    MTAPIRES  IMTGatewayAPI::UserGet(
       const UINT64  login,     // Client login
       IMTUser*      user       // An object of the client record
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.UserGet(
       ulong         login,     // Client login
       CIMTUser      user       // An object of the client record
       )

### Parameters

**login**  
[in] The login of a client.

**user**  
[out] An object of the client login. The user object must first be created using theIMTGatewayAPI::UserCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

The method only copies to the 'user' object the client's login ([IMTUser::Login](../../../Database-Interfaces/Users/IMTUser/Login.md)), group ([IMTUser::Group](../../../Database-Interfaces/Users/IMTUser/Group.md)) and the number of the external system account associated with this gateway ([IMTUser::ExternalAccount*](../../../Database-Interfaces/Users/IMTUser/ExternalAccountGet.md)).

```

---

<a id='main-interface-users-usergetbyaccount-md'></a>
### 195. `Main-Interface/Users/UserGetByAccount.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserGetByAccount

[Previous](UserGet.md) | [Next](UserGroup.md)

# IMTGatewayAPI::UserGetByAccount

Get a client record, which corresponds to the account number in the external trading system.

C++
    
    
    MTAPIRES  IMTGatewayAPI::UserGetByAccount(
       LPCWSTR       account,   // Account number
       IMTUser*      user       // Client record object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.UserGetByAccount(
       ulong         account,   // Account number
       CIMTUser      user       // Client record object
       )

### Parameters

**account**  
[in] The number of the account in an external trading system.

**user**  
[out] An object of the client record. The user object must first be created using theIMTGatewayAPI::UserCreatemethod.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

```

---

<a id='main-interface-users-usergroup-md'></a>
### 195. `Main-Interface/Users/UserGroup.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserGroup

[Previous](UserGetByAccount.md) | [Next](UserLogins.md)

# IMTGatewayAPI::UserGroup

Get the group of a client by the login.

C++
    
    
    MTAPIRES  IMTGatewayAPI::UserGroup(
       const UINT64  login,     // Client login
       MTAPISTR&     group      // Client group
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.UserGroup(
       ulong         login,     // Client login
       out string    group      // Client group
       )

### Parameters

**login**  
[in] The login of a client.

**group**  
[out] The name of a user group to which the client belongs.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

A gateway can only access groups, which are specified in the gateway configuration (the Groups tab in MetaTrader 5 Administrator the Groups tab). To get the list of available groups, use [IMTConGateway::Group*](../../../Configuration-Interfaces/Gateways/IMTConGateway/GroupNext.md) methods.

```

---

<a id='main-interface-users-userlogins-md'></a>
### 195. `Main-Interface/Users/UserLogins.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserLogins

[Previous](UserGroup.md) | [Next](../Configuration-Databases.md)

# IMTGatewayAPI::UserLogins

Returns an array of logins of the clients available to the gateway.

C++
    
    
    MTAPIRES  IMTGatewayAPI::UserLogins(
       UINT64*&      logins,       // An array of client logins
       UINT&         logins_total  // The number of logins
       )

.NET
    
    
    ulong[]  CIMTGatewayAPI.UserLogins(
       out MTRetCode res           // Response code
       )

### Parameters

**logins**  
[out] An array of client logins.

**logins_total**  
[out] The number of logins in the logins array.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

A gateway can only access groups, which are specified in the gateway configuration (the Groups tab in MetaTrader 5 Administrator the Groups tab). To get the list of available groups, use [IMTConGateway::Group*](../../../Configuration-Interfaces/Gateways/IMTConGateway/GroupNext.md) methods.

```

---

<a id='main-interface-users-usersubscribe-md'></a>
### 195. `Main-Interface/Users/UserSubscribe.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserSubscribe

[Previous](UserCreateAccount.md) | [Next](UserUnsubscribe.md)

# IMTGatewayAPI::UserSubscribe

Subscribe to events associated with changes in the client base.

C++
    
    
    MTAPIRES  IMTGatewayAPI::UserSubscribe(
       IMTUserSink*  sink      // A pointer to the IMTUserSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.UserSubscribe(
       CIMTUserSink  sink      // CIMTUserSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTUserSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error has occurred, which corresponds to the response code.

### Note

Subscribing to events is thread safe. One and the same interface [IMTUserSink](../../../Database-Interfaces/Users/IMTUserSink.md) cannot subscribe to events twice - in this case the response code [MT_RET_ERR_DUPLICATE](../../../Return-Codes/Common-errors.md) is returned.

  * [OnUserAdd](../../../Database-Interfaces/Users/IMTUserSink/OnUserAdd.md)
  * [OnUserUpdate](../../../Database-Interfaces/Users/IMTUserSink/OnUserUpdate.md)
  * [OnUserDelete](../../../Database-Interfaces/Users/IMTUserSink/OnUserDelete.md)
  * [OnUserSync](../../../Database-Interfaces/Users/IMTUserSink/OnUserSync.md)



```

---

<a id='main-interface-users-usertotal-md'></a>
### 195. `Main-Interface/Users/UserTotal.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserTotal

[Previous](UserUnsubscribe.md) | [Next](UserGet.md)

# IMTGatewayAPI::UserTotal

Get the total number of users in groups available to the gateway.

C++
    
    
    UINT  IMTGatewayAPI::UserTotal()

.NET
    
    
    uint  CIMTGatewayAPI.UserTotal()

### Return Value

The number of users in groups available to the gateway.

### Note

A gateway can only access groups, which are specified in the gateway configuration (the Groups tab in MetaTrader 5 Administrator the Groups tab). To get the list of available groups, use [IMTConGateway::Group*](../../../Configuration-Interfaces/Gateways/IMTConGateway/GroupNext.md) methods.

```

---

<a id='main-interface-users-userunsubscribe-md'></a>
### 195. `Main-Interface/Users/UserUnsubscribe.md`

```markdown
[🏠 Document Start](../../../README.md) / [Gateway API](../../README.md) / [Main Interface](../../Main-Interface.md) / [Users](../Users.md) / UserUnsubscribe

[Previous](UserSubscribe.md) | [Next](UserTotal.md)

# IMTGatewayAPI::UserUnsubscribe

Unsubscribe from events associated with changes in the client base.

C++
    
    
    MTAPIRES  IMTGatewayAPI::UserUnsubscribe(
       IMTUserSink*  sink      // A pointer to the IMTUserSink object
       )

.NET
    
    
    MTRetCode  CIMTGatewayAPI.UserUnsubscribe(
       CIMTUserSink  sink      // CIMTUserSink object
       )

### Parameters

**sink**  
[in] A pointer to the object that implements theIMTUserSinkinterface.

### Return Value

An indication of successful completion is the [MT_RET_OK](../../../Return-Codes/Successful-completion.md) response code. Otherwise, an error code will be returned.

### Note

This method is pared to [IMTGatewayAPI::UserSubscribe](UserSubscribe.md). If an attempt is made to unsubscribe from the interface to which it has not subscribed, [MT_RET_ERR_NOTFOUND](../../../Return-Codes/Common-errors.md) error is returned.

```

---
