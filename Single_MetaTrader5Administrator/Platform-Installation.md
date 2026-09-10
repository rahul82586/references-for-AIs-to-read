# 📁 Platform-Installation

- **Generated:** 2026-09-10 12:32
- **Total Files:** 9
- **Source:** `C:\Users\DELL\Desktop\New folder (2)\MT5-Administrator\MetaTrader5Administrator\MetaTrader-5-Trading-Platform\Platform-Installation`

---

## 📑 Table of Contents

1. [Activation.md](#activation-md)
2. [Console-Setup.md](#console-setup-md)
3. [Fast-Deployment.md](#fast-deployment-md)
4. [Installation.md](#installation-md)
5. [Platform-Moving.md](#platform-moving-md)
6. [Platform-Uninstall.md](#platform-uninstall-md)
7. [System-Preparation.md](#system-preparation-md)
8. [System-Requirements.md](#system-requirements-md)
9. [White-Label.md](#white-label-md)

---

## 🌲 Project Structure

```
Platform-Installation/
├── Activation.md
├── Console-Setup.md
├── Fast-Deployment.md
├── images/
│   ├── access_permit_icon.png
│   ├── activate_icon.png
│   ├── activate_license.png
│   ├── activation_delete_button.png
│   ├── activation_servers.png
│   ├── add_button.png
│   ├── backup_server_backuping_icon.png
│   ├── backup_server_backuping_icon2.png
│   ├── configure_server_connection.png
│   ├── configure_server_performance.png
│   ├── configure_server_power.png
│   ├── configure_server_recycle.png
│   ├── configure_server_sound.png
│   ├── configure_server_startup.png
│   ├── configure_server_swap.png
│   ├── configure_server_time.png
│   ├── configure_server_update.png
│   ├── configure_server_wizard_role.png
│   ├── deploy.png
│   ├── deploy_cmd.png
│   ├── deploy_configure.png
│   ├── deploy_configure_1.png
│   ├── deploy_icon.png
│   ├── deploy_menu.png
│   ├── deploy_menu_1.png
│   ├── firewall_rule_create.png
│   ├── firewall_rule_setup.png
│   ├── install_additional_trade_range.png
│   ├── network_add_backup.png
│   ├── next.png
│   ├── next_1.png
│   ├── next_2.png
│   ├── next_3.png
│   ├── next_4.png
│   ├── next_5.png
│   ├── next_6.png
│   ├── next_7.png
│   ├── next_8.png
│   ├── platform_configuration_admin.png
│   ├── platform_configuration_diagram.png
│   ├── platform_installation_finish.png
│   ├── platform_installation_settings.png
│   ├── platform_installation_type.png
│   ├── platform_uninstall.png
│   ├── platform_uninstall_finish.png
│   ├── platform_uninstall_settings.png
│   ├── previous.png
│   ├── previous_1.png
│   ├── previous_2.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   ├── previous_6.png
│   ├── previous_7.png
│   ├── previous_8.png
│   ├── rdp_settings_accounts.png
│   ├── rdp_settings_ip.png
│   ├── rdp_settings_port.png
│   ├── server_config_gui.png
│   ├── server_config_gui_main.png
│   ├── server_config_gui_main_settings.png
│   ├── server_config_gui_main_used.png
│   ├── server_inactive_icon.png
│   ├── switch_to_backup_confirm.png
│   ├── switch_to_bakcup_icon.png
│   ├── switching_to_backup.png
│   ├── white_label_edit.png
│   ├── windows_defender.png
│   ├── windows_defender_folder.png
│   ├── windows_defender_process.png
│   ├── wl_form.png
│   ├── wl_installer_company.png
│   ├── wl_mobile.png
│   ├── wl_mobile_error.png
│   └── wl_servers_temrinal.png
├── Installation.md
├── Platform-Moving.md
├── Platform-Uninstall.md
├── System-Preparation.md
├── System-Requirements.md
└── White-Label.md
```

---

## 📄 Files

<a id='activation-md'></a>
### 9. `Activation.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / Activation

[Previous](Installation.md) | [Next](White-Label.md)

<a id="activation"></a>
# Activation (#activation)

A license given for [installation](../Platform-Installation.md) with the platform distribution is non-activated and has several limitations:

  * Only one trade server (main) can be installed in the system;
  * Not more than 100 users can be created;
  * Not more than 5 groups can be created, including four groups created on default.



After installing the platform and [connecting](../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server.md) to the server via the administrator terminal, go to the [start page](../Platform-Setup/Start-Page.md) and click on "Activate now":

![License Activation](images/activate_license.png)

For launching the activation process, you can also use the "![Activate](images/activate_icon.png) Activate" command of the [Services](../MetaTrader-5-Administrator/User-Interface/Main-Menu/Services.md) menu. The following actions are performed during activation:

  * A request is sent to the update server of the developer company;
  * In case of successful license checking, a new activated license is generated; it is bound to the configuration of server where the platform is installed;
  * Activated [license (#license)](../Platform-Components/Trade-Server/Structure-of-Directories-and-Files.md#license) is sent back to the trade server.



> The number of license activations is limited. Normally, up to five activations are allowed for one license.

<a id="manage"></a>
## Activation Management (#manage)

To view your activations, visit the "[App Store\Licenses](https://support.metaquotes.net/en/market/licenses)" section of the technical support website:

![Information about activated licenses](images/activation_servers.png)

A list of activations of each platform license contains the following data:

  * Server name — the name displayed in client terminals (in the program name, in the Navigator window, etc.). The first part of the name is taken from the appropriate [White Label](White-Label.md), the second one is used from platform settings (specified on the [start page](../Platform-Setup/Start-Page.md)).
  * IP — the IP address from which the platform was activated.
  * Build — current platform build. If the build is shown in red, this means there is a [new version](../Platform-Setup/Live-Update.md) available for the platform. We recommend installing the latest version to ensure the operation stability and to access all the new features of the platform. 
  * Created — platform activation date.
  * Last active — the date of the last platform data update (including the platform build). Platforms send related service information to the server every 24 hours, during [optimization time (#optimization)](../Platform-Setup/Network-cluster/Configuring-Servers.md#optimization). The last activity time is updated each time the data is sent. If no data is received for one month, the date is shown in red, which is a warning about server inactivity. If a platform does not update data for three months, it is automatically removed from the list of available servers in terminals, as well as ["Signals"](https://www.mql5.com/en/signals) and ["Virtual Hosting"](https://www.mql5.com/en/vps) services.



Two types of platform [activations](Activation.md) are available: main (shown in bold) and non-main.

  * Client terminals can only connect to a platform with the main activation.
  * To enable connections of client terminals, the platform sends information about its access points (installed access servers) to the update server every hour. Information is sent to the server regardless of the activation type, but only access points of the main activation are transmitted to terminals.
  * Servers with non-main activation are not shown in the broker selection dialogs when opening accounts through terminals.



To set a platform activation as main, please contact [Service Desk](../Technical-Support.md).

  * If you move the platform to another server and activate it, the new activation will appear in the list as non-main. As soon as you complete the platform preparation, be sure to contact [Service Desk](../Technical-Support.md) to change the activation to main. Otherwise, traders may have problems connecting to the new server, since access points will not be known to client terminals.
  * Desktop terminals receive up-to-date information about access points during each account connection. It is recommended to keep at least one old access point operating during 1-2 weeks after migrating the platform to other equipment/hosting provider, so that terminals can receive such information.
  * Activation is bound to server hardware. In case you change computer configuration, a new activation from the same IP address can appear in the list. If the list of access points has not changed, this will not affect operation with client terminals. However, we recommend that you contact the support team to switch the new activation to the main one.

  
---  
  
Outdated activation can be removed by clicking![Delete](images/activation_delete_button.png). If you do not have enough permissions to delete activations or do not see the server management section, please contact [Service Desk](https://support.metaquotes.net/en/servicedesk).

```

---

<a id='console-setup-md'></a>
### 9. `Console-Setup.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / Console Setup

[Previous](Fast-Deployment.md) | [Next](Platform-Moving.md)

<a id="console-setup"></a>
# Console Setup (#console-setup)

Every executable file (*.exe) of the trading platform servers possesses a certain set of console commands. Using them you can perform common actions with appropriate services in the system, as well set up connection of components when connection via the administrator terminal is impossible.

To start executing console commands, open the "Run" window of the operating system and execute the "cmd" command. In the command line go to the directory where the executable file of one of the servers is located, enter its name and specify one of the console commands. For example:

C:\MetaTrader 5 Platform\Access>mt5access.exe /stop

<a id="common-commands"></a>
## Common Commands (#common-commands)

The following set of console commands perform common actions and is available for executable files of [all servers](../Platform-Components.md):

  * /start — start the service that is connected with this executable file of the server;
  * /stop — stop the service that is connected with this executable file of the server;
  * /restart — restart the service that is connected with this executable file of the server;
  * /console — start the service in the console mode;
  * /install [/name:service_name /display:displayed_name /description:service_description] — install a service associating it with this executable file. For additional parameters you can specify the service name for the operating system, extended (displayed) service name for users, as well its description. If you do not specify any of parameters, the service name will be set by default;
  * /uninstall [/name:service_name] — uninstall a service associated with this executable file, For an additional parameter, you can specify the service name to be uninstalled.
  * /info — show information about the server: internal identifier (ID), own address, address of the main server and binding addresses (for access servers).



> Additional parameters are specified without square brackets. For example: /install /name:mt5access /display:Access server

<a id="setup-of-servers"></a>
## Setup of Servers (#setup-of-servers)

If incorrect settings were specified during the installation of any of components, and connection to the platform via the administrator terminal is impossible, you can re-configure the components using the console command /config. It can be executed on any server except for the main trade server. This command has the following parameters:

  * /main:address:port (for trade servers) or /main_trade:address:port (for other servers) — IP address and port of the main trade server, separated by a colon.
  * /own:address:port — IP address and port of the server you are configuring, separated by a colon.
  * /history:address:port — the IP address and port number of the history server. The parameter is only used when configuring access servers. It enables immediate specification of the history server address, without waiting for it from the main server. This improves the speed and reliability server deployment.
  * /id:identifier — the internal identifier of the server you are configuring.
  * /password:password — the internal password of the server you are configuring.



You can specify multiple addresses separated by commas in the 'main', 'own' and 'history' parameters. For example: /main:192.168.0.1:440,[2a00:1987:1:30::2a]:440.

These parameters are analogous to those specified in the ["Network"](../Platform-Setup/Network-cluster.md) section in the administrator terminal. After the command execution, the earlier specified parameters for the server will be overwritten.

> Example: /config /main:192.168.0.1:440 /own:192.168.0.1:443 /id:3 /password:3jdaLjsQ

<a id="setup-of-servers-in-the-graphical-mode"></a>
### Setup of Servers in the Graphical Mode (#setup-of-servers-in-the-graphical-mode)

In order to start setting up a server in the graphical mode, you should run its executable file with the /gui key from the command line. For example, mt5access64.exe /gui.

![Setup in the graphical mode](images/server_config_gui.png)

Parameters that are set here are the same as in the console mode:

  * Server IPv4\IPv6 address — colon separated IP address and port of the configured server;
  * Server ID — the internal identifier of the server you are configuring;
  * Password — the internal password of the server you are configuring;
  * Main Trade server — IP address and port of the main trade server, separated by a colon.



  * When launching the backup server setup, the Restore command becomes available in the configuration window. It can be used to restore a server that was backed up by the selected server. Find more details about the server recovery [here](../Platform-Components/Backup-Server/Restoring-Server.md).
  * Use only the /gui_main key to configure the main trade server. When using the /gui key, the main server becomes a secondary one.

  
---  
  
<a id="numa"></a>
### Linking to NUMA Nodes (#numa)

You can link specific servers to the required [NUMA nodes](https://en.wikipedia.org/wiki/Non-uniform_memory_access). How to link:

  * Stop the server.
  * Call the command 'mt5trade64.exe /modify /numa_node:X' indicating the node number instead of X. Repeat for other servers.
  * Start the server.



<a id="setup-of-the-main-trade-server"></a>
## Setup of the Main Trade Server (#setup-of-the-main-trade-server)

To configure the main trade server, a separate console command /config_main with the below parameters is used:

  * /main:address:port — IP address and port of the [main trade server](../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md), separated by a colon;
  * /access:address:port — IP address and port of an [access server](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md), separated by a colon;
  * /history:address:port — IP address and port of a [history server](../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md), separated by a colon;
  * /backup:address:port — IP address and port of a [backup server](../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md), separated by a colon;
  * /password:password — the internal password that will be set to all the above mentioned servers.



In addition, [internal IDs (#identifier)](../Platform-Setup/Network-cluster/Configuring-Servers.md#identifier) will be automatically assigned to all servers: "1" to the trade server, "2" to the access server, "3" to the history server, and "4" to the backup server.

<a id="setup-of-the-main-trade-server-in-the-graphical-mode"></a>
### Setup of the Main Trade Server in the Graphical Mode (#setup-of-the-main-trade-server-in-the-graphical-mode)

To start setting up a main trade server in the graphical mode, you should start its executable file with the /gui_main key from the command line. For example, mt5trade64.exe /gui_main.

![Setup in the Graphical Mode](images/server_config_gui_main.png)

The appeared window contains the list of servers which settings are already present at the main trade server. Three commands are provided for managing the servers:

  * Add — add a server configuration;
  * Edit — change configuration of a selected server;
  * Delete — delete configuration of a selected server. When deleting a configuration, the physical deletion of the server form the computer is not performed.



The windows of settings contain the main parameters of servers, that are set through the administrator terminal in the ["Network" (#common)](../Platform-Setup/Network-cluster/Configuring-Servers.md#common) section:

![Settings of Server](images/server_config_gui_main_settings.png)

Additional column Used is displayed for the ranges of accounts, orders and deals. It displays the current use of the range.

![The Range of Accounts](images/server_config_gui_main_used.png)

You can stop using the current range by specifying the last value from Used field in To field. After that, create a new range.

Parameters set when configuring the main trade server are checked for correctness:

  * Adding a duplicate main or history server — there can be only one server of each type in a cluster.
  * Specifying incorrect ranges of logins, orders and deals.
  * Creating more trade servers than allowed by the license. Such servers will not work.
  * Deleting main server (deleting directly or changing its type).
  * Deleting a working trade server.
  * Changing networks settings so that the main server will become inaccessible to the administrator. For example, deleting the last access server.



In all the cases mentioned above the administrator will get the corresponding warning when trying to save the changes.

<a id="rebinding-a-cluster-to-another-ip-address"></a>
## Rebinding a Cluster to Another IP Address (#rebinding-a-cluster-to-another-ip-address)

When changing an IP address on the server the MetaTrader 5 cluster is installed at, rebinding to a new address is done as follows:

  * Execute /gui_main command for the main trading server and replace the addresses of all cluster components with new ones.
  * Execute /gui command for the history server and replace the addresses of the history and main servers with new ones.
  * Execute /gui for the access server and replace the addresses of the access and the main servers with new ones.



```

---

<a id='fast-deployment-md'></a>
### 9. `Fast-Deployment.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / Fast Deployment

[Previous](White-Label.md) | [Next](Console-Setup.md)

# Fast Deployment

The fast deployment function simplifies installation of the platform's additional components. During a conventional server installation, you should specify its settings twice: during the installation itself and when creating its configuration via the Administrator terminal. Instead, you can first create a correct server configuration and then receive a setup file with all the previously specified settings.

Before the deployment, configure the server network parameters: ID and password to be used by other cluster components for connection to the new server, as well as IP addresses to be used by the new server for sending and receiving data. All these parameters, as well as data for connecting to the platform's main server, are specified in the installation package. Thus, all remaining cluster components are able to connect to the new server immediately after the installation allowing you to manage the server via the Administrator terminal.

> The function of deployment is available only for access, backup and additional trade servers.

## Creating and Configuring the Server

Create a server configuration in the [Network](../Platform-Setup/Network-cluster.md) section by clicking ![Add](images/add_button.png) Add. Specify an ID and a password to be used by other cluster components for connection to the new server on the [Common (#common)](../Platform-Setup/Network-cluster/Configuring-Servers.md#common) tab. Specify IP addresses to be used by the new server to send and receive data on the [Network (#network)](../Platform-Setup/Network-cluster/Configuring-Servers.md#network) tab.

> Make sure that your [network parameters (#network-connection)](System-Preparation.md#network-connection) are properly configured and all [required ports (#firewall)](System-Preparation.md#firewall) are open, because instant connection to all required servers within the cluster will be needed during deployment.

![Server Settings](images/deploy_configure.png)

The created server will be marked by a gray icon (for example,![Inactive server](images/server_inactive_icon.png)), which means that the server service is not running in the operating system. In our case, such a service is simply not installed.

## Deployment

Click "![Deploy...](images/deploy_icon.png) Deploy..." in the new server context menu:

![Deploy Server](images/deploy_menu.png)

This will open the deployment dialog. Click Deploy and select a folder where the setup file is to be saved.

![Server Deployment](images/deploy.png)

A file of the following form will be saved to the specified folder: Deploy_ID_ServerName.exe. Here ID is the [internal ID (#identifier)](../Platform-Setup/Network-cluster/Configuring-Servers.md#identifier) of the server, ServerName — name of the server. Copy the file to the required computer, to the directory from which the installed server will operate. After that run it from the command line with the /install key. For example:

D:\MetaTrader 5 Platform\Backup History\Deploy_5_Backup_Server.exe /install  
---  
  
The file will install the server with the parameters pre-configured in the MetaTrader 5 Administrator. The results of deployment are written in a text file Deploy_ID_ServerName.txt, located in the same directory.

![Starting Deployment](images/deploy_cmd.png)

During installation, the availability of a network connection to the main and historical servers of the platform is checked. When installing a backup server, the system additionally checks the connection to the primary server. If the connection cannot be established, the installation is aborted and the relevant message is added to the log. To ignore errors and to install the component anyway, restart the installer with the additional /nochecks switch.

After installation you can [configure other parameters of the server](../Platform-Setup/Network-cluster/Configuring-Servers.md).

## Additional Parameters of Installation

The deployer file can be run with additional parameters specified in the command line:

  * /nogui — in an operating system with UAC (User Account Control) enabled, running the deployer file may require higher privilege (administrator rights) and evoke a window with the corresponding request. When running the deployer file with this parameter, an attempt to acquire higher privilege is not made.
  * /main:address:port — using this parameter, you can redefine the address of the main trade server in the configuration of the server installed.
  * /history:address:port — using this parameter, you can redefine the address of the history server in the configuration of the server installed.
  * /name:name — using this parameter, you can define a short name of the service of the server installed.
  * /display:display — using this parameter, you can define a full name of the service of the server installed.
  * /desc:description — using this parameter, you can define a description of the service of the server installed.



An example of running the file with additional parameters: Deploy_5_AccessSever.exe /install /main:192.168.1.135:433 /name:mt5accesssrv.

  * The server will be automatically configured according to the settings specified for it in the administrator terminal.
  * The server is installed in the folder, from which the deployer was started.
  * After deploying a server you should [restart](../Platform-Setup/Network-cluster/Restarting-and-Stopping-Servers.md) the main trade server.


  * If a component is installed in another subnetwork (different from the one, where the main trade and the history servers are installed), the main trade server and the history server must be accessible via the Internet. Otherwise, the newly installed component will not be able to connect to them.
  * In case of deploying a trade server, a manager account is created on it. It is required for the first connection to the server. The account login and password are saved in the log file of the server (/Logs folder). The log record looks as following: default manager with login '1000' and password 'lfd5fircvs' added

  
---  
  
## Removing the Server

To remove the service of the installed server from the operating system, you can use the corresponding [console command](Console-Setup.md) of the server (/uninstall). After that, the folder where the server was installed, can be removed physically from the disk.

```

---

<a id='installation-md'></a>
### 9. `Installation.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / Installation

[Previous](System-Preparation.md) | [Next](Activation.md)

<a id="installation-of-the-metatrader-5-platform"></a>
# Installation of the MetaTrader 5 Platform (#installation-of-the-metatrader-5-platform)

Before you start platform installation, you need to rent servers from hosting providers keeping in mind [system requirements](System-Requirements.md). Required [preparatory works](System-Preparation.md) should be performed on these servers. After that you can proceed to platform installation:

  * Complete platform installation on the main server
  * First connection to the platform and necessary actions
  * Installation of additional backup servers
  * Additional access servers
  * Additional trade servers
  * Installation of a platform for testing new features and developing own solutions



<a id="full"></a>
## Complete platform installation on the main server (#full)

The platform installer allows you to deploy a required set of servers on one local computer, including the main trade server, its backup server, the history server and the access server. This option should be used during the first platform installation on the main server. After that, you will be able to connect to the platform using the MetaTrader 5 Administrator and proceed to the installation and configuration of additional components.

Run the mt5srvsetup.exe platform installer and select "Full installation":

![Selecting the installation type](images/platform_installation_type.png)

Read the license agreement and, if you agree, check "Yes, I agree with all terms of this license agreement". Next, specify the path to the platform license file *.lic. Information from the license is displayed at this stage, including the product (license expiration date), the company for which the license has been issued, and the domain name.

![Platform Installation](images/platform_installation_settings.png)

At the next stage, specify the installation parameters:

  * Installation folder — click "Browse" and select the folder to which you want to install the trading platform.
  * Program group — specify the group name for the trading platform; this name will be displayed in the Start menu.
  * IP address — choose one of the IP addresses available on the server. Connection to the platform will be established using this address.
  * Profile — choose one of the port profiles for connection. The 441-444 range is used by default, and the port 443 will be used for public access (access server). Other ports are allocated for the trade server, the history server, and the backup server. There are also some additional profiles. For example, the range of 1950-1953, in which port 1950 is used for the access server.



  * If all ports specified in the profiles are occupied by other applications, you should install the platform components one by one. In this case, you can specify any other port manually.


  * Full Installation is not possible if at least one of the ports from the selected range (profile) is busy. In this case, it does not matter what network interface it is used for. The installer checks all available interfaces to prevent any network conflicts. If you receive a message about a busy port during Full Installation, install the platform components one by one.

  
---  
  
A click on the Next button will launch the platform installation process:

![Completing the Installation](images/platform_installation_finish.png)

At the end of the installation procedure, a dialog box will appear showing details for the first connection to the platform using MetaTrader 5 Administrator: a login and password for the automatically created administrator entry, and the address for connection. Be sure to save this data in a safe place, otherwise you will not be able to connect to the platform without this information.

To complete platform installation, press "Finish". After that, a program group specified during installation, with the commands to launch and stop platform components will appear in the Start menu.

<a id="first-connection"></a>
## First connection to the platform and necessary actions (#first-connection)

One [administrator account](../Platform-Setup/Managers.md) with login "1000" and a random password is automatically created during platform installation. These data, as well as the address of the server to connect to, are displayed on the last step of the platform installation. Be sure to save this data in a safe place, because without it you will not be able to connect to the platform using the MetaTrader 5 Administrator.

The password to the automatically created administrator account is also saved in the log file of the main trade server (the /Logs folder).

[Add](../MetaTrader-5-Administrator/Getting-Started/Add-or-Remove-Servers.md) the newly installed platform to the MetaTrader 5 Administrator, and then [connect](../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server.md) to it using the administrator account. For security reasons, you will immediately need to [change your password (#change-password)](../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server.md#change-password).

At the next step, you need to [activate licenses](Activation.md), in order to remove all functional limitations of the platform.

> The password generated for the first administrator account is also used by all components of the platform for internal authentication. If necessary, change it on the [Common (#password)](../Platform-Setup/Network-cluster/Configuring-Servers.md#password) tab of each server.

<a id="backup"></a>
## Installation of additional backup servers (#backup)

Once the main platform part is installed, it is recommended to configure appropriate backup servers. The ability to ensure uninterrupted business operation is one of the main requirements set by financial regulators.

The MetaTrader 5 platform provides a separate component responsible for data security, which is the [backup server](../Platform-Components/Backup-Server.md). It runs in parallel as an exact copy of the primary trade or history server. The state of the backup server is constantly synchronized with the primary server, allowing any time to switch to the backup server. However, the backup creation process is resource efficient:

  * Critical and frequently changing data are synchronized in real time. These include client and trade databases, platform settings, configurations and databases of gateway trade executions.
  * The remaining data are backed up every hour, including mail and news databases, files, executable files and gateways and data feeds, plug-ins, etc.



  * Always install backup servers — it is a mandatory component of the platform. The trade and history servers do not create backups of data bases.
  * Several backup servers can be created for each trade and history server, which reduces the risk of system failure to a minimum.

  
---  
  
During the complete platform installation, a backup server is only created for the main trade server. It is installed on the same computer/disk, where the main components are installed. It only provides the minimum level of protection, for example against the accidental deletion of the main server databases. However, in case of hardware failure, the main and the backup server will be unavailable.

In order to provide a reliable platform operation, it is recommended to manually add backup servers for the history server, as well as additional trade servers (if any). Such backup servers must be installed separately from the main servers, and always on separate computers.

The easiest way to install the server is to configure it first in the MetaTrader 5 Administrator terminal, and then to use the [deployment](Fast-Deployment.md) function.

Before deploying a server, make sure to configure the server network parameters: the password that will be used by other cluster components for connection to the backup server, as well as the IP addresses, through which the new server will send and receive data. All these parameters will be registered in the server installation package. Thus, all remaining cluster components will be able to connect to the backup server immediately after installation, while you will be able to manage the server via the Administrator terminal.

> Make sure that [network parameters (#network-connection)](System-Preparation.md#network-connection) are correctly configured and all the [required ports (#firewall)](System-Preparation.md#firewall) are open. It is important, because during deployment, an instant connection to all the required servers of the cluster will be required.

All other parameters can be configured after installation.

![Server Settings](images/deploy_configure_1.png)

After creating a configuration, run the server deployment command:

![Deploy...](images/deploy_menu_1.png)

After that you will receive an executable file. Copy it to the directory to which you want to install the new server and then run from the command line with the /install key. For example:

D:\MetaTrader 5 Platform\Backup History\Deploy_5_Backup_Server.exe /install  
---  
  
The file will install the backup server with the parameters that were pre-configured in the MetaTrader 5 Administrator. Then you should [configure the rest backup parameters](../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md):

![Backup Settings](images/network_add_backup.png)

When configuring parameters of backup servers, you should find balance between the frequency of backups and the available disk space on the computer where the backup server is installed:

  * Backup time — time of creating file copies. Apart from synchronizing with the main server in real time, the backup server creates [database file copies (#file)](../Platform-Components/Backup-Server/Backup-Features.md#file) on the disk on a daily basis. Such copies allow [restoring (#restore)](../Platform-Components/Backup-Server/Backup-Features.md#restore) the main server status on a specific day.
  * Additional backups — frequency of creating additional file copies. By default, file copies are created every 24 hours, but you can set this to happen more often — once per hour or once per 4 hours. Keep in mind that this will require more server resources and more disk space. This option is only available for the backup of trading servers; backup copies of history servers are always created once every 24 hours.
  * Keep backups — file copies storage period. All backup copies older than a period specified in this field are automatically deleted.
  * Enable tick backups — this parameter should be enabled with caution, because tick data take up too much space. If you back up tick data, set short copy storing period so that they do not consume all the available disk space.



  * Repeat the procedure and install backup servers for other platform components , including the history server and all other trade servers. Install backup servers separately from the main ones, and always on separate computers.


  * Install assess servers close to the backup ones. These access servers will be used for client connections in case the platform switches to the backup servers.

  
---  
  
<a id="access"></a>
## Additional access servers (#access)

It is recommended to install additional access servers in order to improve system performance and reliability. Access servers process client connections, cache data, and protect the platform against DDOS attacks. They also monitor the availability of the trade and history servers to enable the operation of the [automatic failover system (#auto)](../Platform-Components/Backup-Server/Switching-to.md#auto).

Connection to the entire trading platform is only available through access servers. If you decide to use one server, and it fails, neither administrators nor traders will be available to connect to the platform. In addition, the entire connection processing load will be handled by one server, which may affect negatively the system performance.

It is recommended to install several access servers on separate computers. The platform [analyzes the current load](../Platform-Components/Access-Server/Priority.md) on each server, and effectively distributes client connections between them. 

Access servers can be installed using the earlier described deployment procedure. After the installation, configure all other parameters in the [Network cluster](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md) section.

<a id="trade"></a>
## Additional trade servers (#trade)

If the company becomes larger and the number of active clients increases, you can install additional trade servers in order to remove some load from the main server. It is recommended to install an additional trade server in the same data center, where the main and history servers are installed. Trade servers should not be far from the history server, in order to avoid delays when delivering quotes and sending trading operations to external systems through gateways.

After the installation of an additional trade server, it is recommended to install its backup server in a different data center, where the backup servers of the main and history servers are running.

Additional trade servers can be installed using the earlier described deployment procedure. After the installation, configure all other parameters in the [Network cluster](../Platform-Setup/Network-cluster/Configuring-Servers/Access-Server.md) section.

<a id="automatic-creation-of-the-first-administrator-account"></a>
### Automatic creation of the first administrator account (#automatic-creation-of-the-first-administrator-account)

The platform architecture allows an administrator/manager to only work with accounts and databases on the trade server, where the administrator or manager account (its group) is located. For example, when connected to the main server, the administrator/manager cannot create accounts on additional trade servers. In order to connect to the additional trade server and manage accounts on it, the administrator or manager needs to have an account on this server.

During the installation of an additional trade server, one administrator account is automatically created on it. The first free login available in the [range of accounts (#accounts)](../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md#accounts) set for the server will be given to the administrator account:

![Range of accounts](images/install_additional_trade_range.png)

In addition to the administrator account, [groups](../Platform-Setup/Groups.md) linked to this account are also created automatically on the server:

  * demo\demoforex-ID
  * managers\dealers-ID
  * managers\administrators-ID
  * real\real-ID



Here ID is the [internal identifier (#identifier)](../Platform-Setup/Network-cluster/Configuring-Servers.md#identifier) of the added trade server.

  * The administrator account and groups can only be created after you specify the range of accounts. It can be specified when adding a server or when editing it. In other words, once a trade server with the specified account range is added, groups and a manager account are automatically created for this server. If you configure the range before running the deployment, the administrator account and the group will be created during server installation.
  * A password for the manager account is generated randomly. The login and password of the created account are written to the server's log file (the /Logs folder). The following entry is added: default manager with login '1000' and password 'lfd5fircvs' added
  * When you first connect using the automatically created administrator account, you will need to complete the [forced password change (#change-password)](../MetaTrader-5-Administrator/Getting-Started/Connect-to-Server.md#change-password) procedure.

  
---  
  
<a id="launching-the-server"></a>
### Launching the server (#launching-the-server)

For the newly added server to start functioning, you need to restart the entire platform (the main trade server). After the system reboot, the following operations are performed automatically:

  * An account in the manager\administrators-ID group is created for the automatically generated administrator account. If the group does not exist for some reasons, an account will be created in another manager group available on the server.
  * If additional accounts were created in the Manager section before restarting the system, and the logins of these accounts fall into the account range of the added server, accounts in appropriate groups will also be created for them.



<a id="dev-license"></a>
## Installation of a platform for testing new features and developing own solutions (#dev-license)

In addition to the main operating platform, you can install a test (developer) platform for free. Use it to test new platform settings and develop applications using MetaTrader 5 API, without affecting workflow processes and real client operations. It is also recommended to use this platform for installing updates released in beta mode. This will allow you to explore new features in advance and test the operation of third-party applications before updating your main platform.

Please contact [Service Desk](../Technical-Support.md) to receive the test platform license. 

A test license is a complete analog of the main license (including the limitation on the number of accounts), but it has several specific features:

  * The server name in the license contains "Test". This name is displayed in all terminals.
  * [Activations of servers (#manage)](Activation.md#manage) installed under the test license cannot be set as main.



The following limitations apply to servers installed under the test license:

  * The server is not included in the list of available servers in the desktop terminal. To connect to the server, specify the access server address manually.
  * Connection to the server from mobile terminals and the [web terminal](../Platform-Components/WebTerminal.md) is not possible.
  * The server does not allow sending [push notifications](https://support.metaquotes.net/en/docs/mt5/manager/push_notifications) through the Manager terminal and API.
  * [Virtual hosting](https://www.mql5.com/en/vps) cannot be allocated for an account opened on the server with the test license.
  * An account opened on the server with the test license cannot be registered as a [trading signal](https://www.mql5.com/en/signals).



> For application development using [MetaTrader 5 API](https://support.metaquotes.net/en/docs/mt5/api), the platform provides [debug versions of the trading and history servers](https://support.metaquotes.net/en/articles/437) (regardless of the license type).

```

---

<a id='platform-moving-md'></a>
### 9. `Platform-Moving.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / Platform Moving

[Previous](Console-Setup.md) | [Next](Platform-Uninstall.md)

# Platform migration to new hardware

If you move the platform to other hardware/hosting provider, in addition to proper platform installation and configuration, it is important to perform a number of actions to ensure uninterrupted service for traders.

## Migration via a backup server

The back-up server replicates the main server data in real time and features its full copy. At any time you can switch to using it manually — this is a quick and automatic procedure. In addition to emergency cases, the procedure can be used for migrating servers to new hardware.

[Install the backup server (#backup)](Installation.md#backup) on the computer, to which you plan to migrate the server. After installation, run it for a few days on the new hardware to make sure it operates well.

Restart the backup server right before you switch to it. This will help avoid loss of data [backed up once an hour](../Platform-Components/Backup-Server/Backup-Features.md). As long as the server copies data, its icon will display ![Backup in process](images/backup_server_backuping_icon.png)(the icon will look like![Backup in process](images/backup_server_backuping_icon2.png)). Wait until the process is completed and run the "![Switch to backup server](images/switch_to_bakcup_icon.png)Switch to backup server" command in the context menu:

![Switching to the backup server](images/switching_to_backup.png)

To avoid accidental switching, the platform requires an additional confirmation. In the dialog that appears, enter the required characters and click "Switch".

![Confirming the switching to the backup server](images/switch_to_backup_confirm.png)

After the procedure is complete, you will see that the main server and the backup server have swapped their places in the Network section:

Run the same procedure for all other history and trade servers. Then [install new backup servers (#backup)](Installation.md#backup) and [access servers (#access)](Installation.md#access). This can be conveniently done using the [fast deployment](Fast-Deployment.md) procedure.

  * Desktop terminals receive up-to-date information about access points during each account connection. It is recommended to keep at least one old access point operating during 1-2 weeks after migrating the platform to other equipment/hosting provider, so that terminals can receive such information.
  * Server migration must only be performed in non-trading hours. When switching to the backup server, it does not copy data which the main server continues to receive.
  * In order to prevent important data from being lost, trading operations and changes in the client base are not allowed on the main server right after the start of switching to the backup server. The ban is valid for one minute. If the platform fails to switch to a backup server within this period, the ban is removed.

  
---  
  
## Platform activation after migration

When migration is complete, go to "Services" menu and click "Start Live Update". Go to the [App Store\Licenses](https://support.metaquotes.net/en/market/licenses) section and make sure the activation is available in the list. Two types of platform [activations](Activation.md) are available: main and non-main.

  * Client terminals can only connect to a platform with the main activation.
  * To enable connections of client terminals to the platform, the platform sends information about its access points (installed access servers) to the server every hour. Information is sent to the server regardless of the activation type, but only access points of the main activation are transmitted to terminals.
  * Servers with non-main activation are not shown in the broker selection dialogs when opening accounts through terminals.



Thus, to ensure full-featured platform operation, you need to set the new activation as main. To do this, please contact [Service Desk](../Technical-Support.md) after completing platform installation.

## Update of Installers

When switching an activation to the main type, support specialists will recompile the client terminal installer for you, i.e. they will include new access points. If you distribute the installer file by yourself, be sure to download its new version from the [Download](https://support.metaquotes.net/en/download) section and update the file on your resources.

> To allow your traders to download the latest installer version any time, we recommend providing them direct terminal download links from the "Download" section. Thus, you will not need to update the files on your resources manually.

```

---

<a id='platform-uninstall-md'></a>
### 9. `Platform-Uninstall.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / Platform Uninstall

[Previous](Platform-Moving.md) | [Next](../Platform-Components.md)

# Platform Uninstall

To remove the entire platform or one of its components, start file uninstall.exe located in the program directory or execute the "Uninstall" command in the corresponding group of programs in the "Start" menu. The following window will appear after that:

![Platform uininstall](images/platform_uninstall.png)

In the greeting window, read the deinstallation warning. If you are sure that want to continue the deinstallation process, press "Next".

> When a platform is removed, configurations and databases are not removed on default. In order to perform the full removal, enable the corresponding option on the next deinstallation stage.

![Parameters of deinstallation](images/platform_uninstall_settings.png)

All currently installed platform components are shown in the left part of the window. Tick off ![Selected Server](images/access_permit_icon.png) servers that you want to remove. Information about the component selected in the tree-like list is shown in the right part of the window. The following details are shown:

  * Server address — IP address of a selected server;
  * Server port — port of a selected server;
  * Server ID — ID of a selected server used for its internal identification;
  * Service name — name of the service, under which the server works in the operating system.



  * To delete the server configurations and data bases, select "Delete server data bases". Be maximally attentive with this option, because in this case data recovery will be impossible. However, if data bases were not deleted, the platform can be recovered then with all the data and configurations.
  * The option of data base deletion is enabled separately for each separate server.

  
---  
  
After you press "Next" all the selected platform components will be deleted.

![Deinstallation completion](images/platform_uninstall_finish.png)

To complete the deinstallation process press "Done".

```

---

<a id='system-preparation-md'></a>
### 9. `System-Preparation.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / System Preparation

[Previous](System-Requirements.md) | [Next](Installation.md)

<a id="system-preparation"></a>
# System Preparation (#system-preparation)

An important issue that directly affects the security and stability of the trading platform is the configuration and optimization of your computer with the operating system. This section highlights the main stages of the process:

  * [Configuring the user interface (#graphics)](System-Preparation.md#graphics)
  * [Disabling server roles (#roles)](System-Preparation.md#roles)
  * [Removing unneeded programs (#programs)](System-Preparation.md#programs)
  * [Configuring system updates (#update)](System-Preparation.md#update)
  * [Disabling time synchronization (#time)](System-Preparation.md#time)
  * [Configuring network connections (#network-connection)](System-Preparation.md#network-connection)
  * [Configuring Windows firewall (#firewall)](System-Preparation.md#firewall)
  * [Disabling sounds (#sound)](System-Preparation.md#sound)
  * [Configuring general performance parameters (#performance)](System-Preparation.md#performance)
  * [Configuring files deletion without moving them to the Recycle Bin. (#recycle)](System-Preparation.md#recycle)
  * [Configuring remote access (#remote)](System-Preparation.md#remote)
  * [Configuring antivirus software (#antivirus)](System-Preparation.md#antivirus)



  * After completing configurations, restart the server.
  * Please note that these are only recommendations. Use them at your discretion depending on your specific circumstances and needs.

  
---  
  
<a id="graphics"></a>
## Graphical interface (#graphics)

First, it is recommended to configure a graphical user interface of the operating system. You should disable anti-aliasing, shadows, menus, transition effects, etc. These settings allow for fast working with the server in remote access.

> Additionally, set blank page as a home page in the Internet Explorer options.

<a id="roles"></a>
## Disabling server roles (#roles)

Disable unnecessary server roles using the server configuration wizard. Launch it via the Administration section and pass through all the steps clicking Next till you see the list of server roles. If there is any active role, select it and click "Next." Skip the next step for configuring the system components by clicking Next. Check the list of removed roles on the confirmation step and click Remove.

![Selecting a server role](images/configure_server_wizard_role.png)

<a id="programs"></a>
## Removing unneeded programs (#programs)

Uninstall any unnecessary programs that can slow down the trading platform or disrupt its security:

  * Web server (Internet Information Server, Apache, etc.);
  * Mail server, DNS server, SNMP, etc.;
  * Databases (Oracle, MSSQL, etc.);
  * Various development environments (IDE), compilers, etc.;
  * .NET and Java environments;
  * Various control agents from the server manufacturer (usually, this is an entire set of default programs) designed to remotely monitor the server.



Launch the wizard for installing and deleting programs. Move to "Uninstall or change a program" and remove unnecessary programs. Remove programs as you see fit depending on your needs and resource efficiency.

<a id="update"></a>
## Configuring system updates (#update)

Enable auto update with manual installation confirmation in the Control Panel. Fully automated mode is not recommended since Windows does not allow selecting the update installation day. It is recommended to install updates on weekends when the server load is minimal.

![Auto update](images/configure_server_update.png)

> Before installing the platform, you should install all necessary updates for your operating system.

<a id="time"></a>
## Disabling time synchronization (#time)

System time synchronization should be performed only by the MetaTrader 5 main trade server on the server where the trading platform is installed. Windows Time should be disabled.

The MetaTrader 5 built-in time synchronization service verifies and corrects time (if necessary) once per hour.

In order to disable time synchronization in the operating system, open the "Date and Time" section of the Control Panel. Go to the "Internet Time" tab, enter 127.0.0.1 to the Server field and unflag the automated synchronization:

![Disabling time synchronization](images/configure_server_time.png)

> If the address of the time synchronization server is not specified in the [time settings](../Platform-Setup/Time.md) of the platform, the Windows Time service is automatically disabled in the operating system when MetaTrader 5 servers are launched.

<a id="network-connection"></a>
## Configuring network connections (#network-connection)

Right-click on the active network connection and select Properties:

![Configuring network connections](images/configure_server_connection.png)

On the Networking tab, remove all components except for TCP/IP v4, TCP/IP v6 and Link-Layer Topology Discovery* protocols. They are helpful when configuring the routing.

<a id="firewall"></a>
## Configuring Windows firewall (#firewall)

The [platform installer](../Platform-Installation.md) (including the one used during the [quick deployment](Fast-Deployment.md)) automatically adds permissions for the necessary ports to the Windows firewall.

If an additional port should be opened for your platform configuration, go to the Control Panel — Windows Firewall — Additional settings. Create a new inbound rule and select:

  * Program — in case you want to allow connections for a specific application, for example a gateway.
  * Port — if you want to open certain ports regardless of an application.



![Creating an inbound rule for a port in the firewall](images/firewall_rule_create.png)

Next, set the port number and select "Allow the connection":

![Configuring an inbound rule for a port in the firewall](images/firewall_rule_setup.png)

Depending on the location of your PC, specify the profile the rule is applied for: domain, private network or public network. At the last stage, enter a name for the rule.

For each component of the platform, the list of ports that should be allowed is different:

<a id="access-server"></a>
### Access Server (#access-server)

Ports for outgoing connections | Reason  
---|---  
Ports, on which [trade servers](../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md) work. | Access servers rout clients' connections to trade servers. In case with the main trade server, additionally configuration files are updated and [time is synchronized (#synchronization)](../Platform-Setup/Time.md#synchronization).  
Port, a [history server](../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md) works on. | Receiving news, quotes and [updates](../Platform-Setup/Live-Update.md).  
Port 443. | Connection to MetaQuotes' Updates server (https://updates.metaquotes.net).  
Ports for incoming connections | Reason  
Port the access server works on ([Bindings (#network)](../Platform-Setup/Network-cluster/Configuring-Servers.md#network)). | These ports will be listened to for receiving clients' connections.  
  
<a id="backup-server"></a>
### Backup Server (#backup-server)

Ports for outgoing connections | Reason  
---|---  
Port of the [main trade server](../Platform-Setup/Network-cluster/Configuring-Servers/Trade-Server.md). | Through the main server, configuration files are updated, as well time is synchronized.  
Port of the server, whose [backups are made (#backup)](../Platform-Setup/Network-cluster/Configuring-Servers/Backup-Server.md#backup). | Backup copying of the server data.  
Port, on which a [history server](../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md) works. | Receiving updates.  
Ports, on which [gateways](../Platform-Setup/Gateways.md) are running. | Backing up gateway data.  
Port 443. | Connection to MetaQuotes' Updates server (https://updates.metaquotes.net).  
[Access server (#network)](../Platform-Setup/Network-cluster/Configuring-Servers.md#network) ports | Monitoring the availability of the backup server if [automatic switch (#auto)](../Platform-Components/Backup-Server/Switching-to.md#auto) to the backups server is enabled.  
  
<a id="trading-server"></a>
### Trading Server (#trading-server)

Ports for outgoing connections | Reason  
---|---  
Port 25. | Sending [reports (#reports)](../Platform-Setup/Groups/Group-Settings.md#reports) to the mail server.  
Port 37. | [Time synchronization (#synchronization)](../Platform-Setup/Time.md#synchronization) by the TIME protocol (for the main server).  
Port 123. | Time synchronization by the NTP protocol (for the main server).  
Port of the main trade server. | Receipt of configuration files and time synchronization (for servers other than the main).  
Port, on which a history server works. | Receiving quotes and updates.  
Ports, on which [gateways](../Platform-Setup/Gateways.md) are running. | Work with gateways: receiving quotes, trading.  
Port 443. | Connection to MetaQuotes' Updates server (https://updates.metaquotes.net).  
Ports for incoming connections | Reason  
Port where the trade server works. | This port is required for the main trade server to connect all other components. For non-main servers it is required for connecting access servers.  
  
<a id="history-server"></a>
### History Server (#history-server)

Ports for outgoing connections | Reason  
---|---  
Port 443. | Connection to MetaQuotes' Updates server (https://updates.metaquotes.net).  
Port of the main trade server. | Receipt of configuration files and time synchronization.  
Ports, on which data feeds work. | Ports for [data feeds](../Platform-Setup/Data-Feeds.md) that establish connection to remote servers. For example, [MetaTrader4Feeder](../Platform-Components/Data-Feeds/MetaTrader-4-Feeder.md) (port 443 is used on default) and [TCNewsFeeder](../Platform-Components/Data-Feeds/Trading-Central-News-Feeder.md) (FTP ports 20 or 21 are used on default).  
Ports, on which remote data feeds work. | Port numbers depend on the [data feeds](../Platform-Components/Data-Feeds/Remote-Datafeed.md) that are connected.  
Ports for incoming connections | Reason  
Port, on which the [history server](../Platform-Setup/Network-cluster/Configuring-Servers/History-Server.md) works. | This port is required for connecting other components of the platform.  
Ports, on which data feeds work. | Ports, on which [data feeds](../Platform-Setup/Data-Feeds.md) work, that receive external connections from remote servers. For example, [DJPrimeTassNewsFeeder](../Platform-Components/Data-Feeds/Dow-Jones-Prime-Tass-News-Feeder.md) (port 20000 is used on default).  
  
<a id="sound"></a>
## Disabling sounds (#sound)

Disable sounds for the server the trading server is installed at. Open the Sound section in the Control Panel:

![Disabling sounds](images/configure_server_sound.png)

Select "No Sounds" in the list of sound schemes and click OK.

<a id="performance"></a>
## Configuration general performance parameters (#performance)

Open the Control Panel — System — System Properties — Advanced — Performance settings. Select "Adjust for best performance" on the "Visual Effects" tab:

![Performance settings](images/configure_server_performance.png)

On the Advanced tab, click Change and enter the value of the initial swap file size equal to its maximum value.

![Configuring the swap file](images/configure_server_swap.png)

Return to the System Properties — Advanced and open the startup and recovery settings:

![Startup and recovery settings](images/configure_server_startup.png)

Disable the "Time to display list of operating systems" option. Set "Write debugging information" to None.

From the control panel, navigate to Hardware — Power Options. Select maximum performance mode:

![Select maximum performance mode in power settings](images/configure_server_power.png)

<a id="recycle"></a>
## Configuring files deletion without moving them to the Recycle Bin (#recycle)

In order to ensure the files are deleted immediately, click Properties in the bin's context menu. Select "Don't move files to the Recycle Bin. Remove files immediately when deleted":

![Configuring files deletion without moving them to the Recycle Bin](images/configure_server_recycle.png)

<a id="configurator"></a>
## Server Configurator (#configurator)

The "Server Configurator" program is specially designed to facilitate the server preliminary configuration process by automating the manual work of terminating various services, system configuration via the registry and deleting temporary and unnecessary information from the disks. You can download this utility from the following link <https://support.metaquotes.net/spfiles/srvcfg.exe>. The program does not require installation, it can be simply launched through the EXE file. Go through all the steps enabling all the flags. A more detailed description of the Server Configurator can be found in the article "[Using the Server Configurator](https://support.metaquotes.net/en/articles/15)".

<a id="remote"></a>
## Configuring remote access (#remote)

> Keep the data for the remote access to the server in a safe place and do not disclose them to anyone without particular reason.

Blocking RDP connections for accounts having no password. Accounts with no entry password should not have permission for remote access to the server. Open the Control Panel — Administrative Tools — Local Security Policy — Security Options. Enable the parameter "Accounts: Limit local account use of blank passwords to console logon only".

![Blocking RDP connections for accounts having no password](images/rdp_settings_accounts.png)

Changing a standard port for remote connection. In order to protect against the attacks monitoring "well-known" ports, change the port for the Remote Desktop Protocol. Open the registry editor (regedit), go to HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp and find the Port Number parameter. Double-click on it, select the decimal system in the new window and set the necessary port as the value.

![Changing the standard port for remote connection](images/rdp_settings_port.png)

  * The specified port should be permitted in the [Windows Firewall (#firewall)](System-Preparation.md#firewall).
  * In order to remotely connect to the server, specify the new port after an IP address separated by a colon. For example, 10.59.162.3:5000.

  
---  
  
Limitation of IP address list for remote connection. As an additional security measure, you can restrict the list of IP addresses that can be used to remotely connect to the server. For example, you can allow connection only from your office's IP addresses.

Open Windows Firewall and find "Remote Desktop - User Mode (TCP-In)" in the list of inbound rules. There may be several such rules depending on the number of network profiles. Open the one you need and go to Scope tab. In the "Remote IP address" section, select "These IP addresses" and add the necessary ones to the list:

![Limiting the list of IP addresses for remote connection](images/rdp_settings_ip.png)

<a id="antivirus"></a>
## Configuring antivirus software (#antivirus)

If antivirus software is used on your server, add to its exclusions the system processes of the MetaTrader 5 platform, as well as its installation directory. Constant monitoring by antivirus software reduces platform performance.

Here is an example of adding exclusions in Windows Defender, which is a built-in antivirus software used on Windows Server 2016. Open Windows Settings — Updates and Security — Windows Defender. Go to "Exclusions" and click "Add an exclusion".

![Configuring exclusions in Windows Defender](images/windows_defender.png)

Select "Exclude folder" and choose the platform installation directory.

![Adding an exclusion for the platform installation directory](images/windows_defender_folder.png)

Click "Exclude process .exe, .com or .src". Specify the name of the platform component process in the window that opens. You can specify the name of the server executable file (for example mt5trade64.exe) or the name of the process (for example mt5msrv).

![Add an exclusion for the platform installation process](images/windows_defender_process.png)

Similar exclusions should be added for all installed components of the cluster. The default names of the services are:

  * mt5msrv — the main trade server
  * mt5tsrv — an additional trade server
  * mt5asrv — an access server
  * mt5bsrv — a backup server
  * mt5hsrv — a history server



If several components of the same type are installed, a digit is added to the service name. For example, mt5tsrv5. The list of installed processes can be viewed in the task manager.

```

---

<a id='system-requirements-md'></a>
### 9. `System-Requirements.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / System Requirements

[Previous](../Platform-Installation.md) | [Next](System-Preparation.md)

<a id="system-requirements"></a>
# System Requirements (#system-requirements)

The MetaTrader 5 platform components are recommended to be installed on dedicated servers rented from hosting companies.

<a id="hardware"></a>
## Hardware (#hardware)

| Minimum requirements | Recommended requirements  
CPU | Intel i7 12xx or AMD Ryzen 9 5900 series, quad-core or higher | Intel Xeon Silver 43XX or AMD EPYC 40XX  
RAM | No less than 16GB | No less than 32GB  
Disk | RAID-1 array with 2 x 1 TB disks | RAID-1 array with two 1 TB SSD/NVMe disks for the trade server and the history server, RAID-1 array with 2 x 1 TB for backup servers  
Network | Both download and upload speed no less than 100 Mbps | Both download and upload speed no less than 1 Gbps  
Operating System | Windows Server 2022 Standard x64 or newer | Windows Server 2025 Standard / Server Core edition  
  
  * The processor must support [AVX2](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions) instructions to enable platform installation.


  * Choose a server configuration depending on the number of clients, financial instruments and the density of quotes stream. When databases grow, causing an increased load on the trading platform, event the initially recommended configuration may be fail to cope with such load.
  * Due to the fact that the backup server is basically a duplicate of the main trading server, it is desirable that the configuration of the backup server is similar or even identical to the configuration of the main server. It's not recommended to place the backup server at the same hosting company as the main server, as it may happen that the entire network of the provider will be unavailable. Locating the servers at different hosting companies increases data security and the resiliency of the system.
  * History server processes and stores a huge volume of information. Due to this fact, important criteria for it are disk volume and disk read/write speed.

  
---  
  
<a id="additional-requirements"></a>
## Additional Requirements (#additional-requirements)

  * No third-party software for system time synchronization is allowed.
  * Use virtualization if you have control over the hypervisor and can ensure enough resources for the virtual machine running MetaTrader 5. At least 8 logical cores must be available to the virtual machine (virtual processors are specified here, unlike physical ones used for dedicated servers). The machine should support the Over-Provisioning technology and have the disk speed of no less than 30 MB/s.
  * Configure BIOS on the server to run low-latency applications: turn all the energy saving features off (including CPU C-state), configure memory settings to the 'High Performance' state.



<a id="recommended"></a>
## Recommended basic cluster configuration (#recommended)

We recommend renting at least two servers. It is advisable to have servers that are physically located in different data centers. One server is to be used as the main one. The second server is used as the backup one. The main server data is to be replicated to it in real time. Thus, even if one of the hosting providers has troubles, you will be able to restore the platform on the backup server. This will allow you to minimize risks, while the probability of failure in both data centers is very small.

The following platform components should be installed on the main and backup servers:

Main server | Standby server  
---|---  
Main trade server History server Access server | Backup server for the main trade server Backup server for the history server Access server  
  
Components can be installed in different physical servers within one data center, in order to provide a greater platform performance.

![The recommended basic platform configuration](images/platform_configuration_diagram.png)

In MetaTrader 5 Administrator, suggested configuration looks as follows:

![Recommended basic platform configuration](images/platform_configuration_admin.png)

It is strongly recommended to install the history server close to trade servers in order to avoid delays when delivering quotes and sending trading operations to external systems through gateways.

```

---

<a id='white-label-md'></a>
### 9. `White-Label.md`

```markdown
[🏠 Document Start](../../README.md) / [MetaTrader 5 Trading Platform](../../MetaTrader-5-Trading-Platform.md) / [Platform Installation](../Platform-Installation.md) / White Label

[Previous](Activation.md) | [Next](Fast-Deployment.md)

<a id="white-label"></a>
# White Label (#white-label)

White Label refers to the branding of the desktop terminal of the trading platform for a specific brokerage company. The White Label includes the company's name, contact details, logos, and other MetaTrader 5 terminal settings.

The client-side part of the platform also includes MetaTrader 5 mobile terminals for iPhone and for Android, as well as the a web terminal that provides account access via a web browser. If these components were not purchased together with the platform, you can [ordered then separately](https://support.metaquotes.net/en/market/product/248) at any time. Please note that no appearance modifications (branding/white labeling) are applied to these components.

> White Label applies exclusively to the MetaTrader 5 desktop client terminal. The Manager and Administrator terminals remain standard and are not subject to customization.

<a id="terminal-wl"></a>
## White Label for the Client Terminal (#terminal-wl)

After the platform purchase, a support ticker will be automatically created in the [Service Desk](https://support.metaquotes.net/en/servicedesk) section of the technical support site. This ticket will include an online form used for creating the White Label. The ticket will allow you to track the delivery status and provide additional information if necessary.

The online form is located in the body of the ticket, directly beneath the subject line.

![White Label form](images/wl_form.png)

  * The fields marked in red are mandatory and must be completed. These include: company address, website, name, short name, server name, and logos.
  * All terminal information (branding, images, server name) must match the company's name. Promotional slogans are not allowed in images unless the company holds a valid legal registration or license for their use.
  * If you do not yet have ready-made logos, you may use the default MetaQuotes logos. Logos and other details can be updated later. To do this, simply open the White Label editing form from the [Download](https://support.metaquotes.net/en/download/mt5) page. The corresponding link appears when you hover your cursor over the terminal name.


  * The "Custom Files," "Servers," and "Documents" sections are available only when editing the White Label via the [technical support website](https://support.metaquotes.net/en/market/whitelabel/mt5). These sections cannot be completed during the initial platform order.

  
---  
  
<a id="the-about-window"></a>
### The About window (#the-about-window)

In this tab, specify your company name, contact details, logo, and program name. This information will be visible to traders in the "About" window of your terminal. You can edit the relevant fields directly within the "About" window. When you hover the cursor over each field, a tooltip will appear explaining what information should be entered.

Element | Description  
---|---  
Company name | The name of the company for which the White Label is being created. By default, this field is populated with the company name provided during contract signing. Scanned copies of company documents can be uploaded in the Documents tab.  
Address | The registered office address of the company, as specified in the KYC form. The address can be specified in two lines. Use the special character \n to insert a line break.  
Phone | Phone number. You may provide additional contact information beyond just the company phone number. The data can be split into two lines using the special character \n. For example: Tel : +1 xxx xxxxxx\nFax: +1 xxx xxxxxx Phone numbers should be specified in the standard international format.  
Site | The URL of your company's website, for example: www.metaquotes.net Do not include the "https" protocol prefix; it will be added automatically. Only one website address can be entered; additional links will not be functional.  
E-mail  | The e-mail address of your company's technical support service.  
Logo | A BMP image with 24-bit color depth. The image dimensions must not exceed 131 pixels in width and 151 pixels in height. To upload a logo, click the Select button and choose an image file in the dialog window. After uploading, you can center the image by clicking the corresponding button. To use a standard MetaQuotes logo, click the Default button ([archive with MetaQuotes logos](https://support.metaquotes.net/spfiles/metatrader4/forms/allimages.zip)).  
Program name | The name is generated based on the company name or registered trademark (brand). It is used as:

  *     * the title of the client terminal window
    * the name of the terminal installation directory and Start menu group
    * the label under the desktop shortcut

If you want to use the word "MetaTrader" in the program name, it must be written exactly as: MetaTrader (as one word, with capital "M" and "T").  
  
The About window always displays the MetaQuotes Ltd copyright notice, a link to the company's website, and a link to the End-User License Agreement (EULA).

<a id="the-installer-window"></a>
### The Installer window (#the-installer-window)

In this section, you can specify your company logo to be displayed in the terminal installation window, as well as the icon under which your terminal will operate.

Element | Description  
---|---  
Banner | A BMP image with 8-bit color depth (256 colors), with exact dimensions of 500 pixels wide by 60 pixels high. You can create a banner by combining the default MetaQuotes logo with your company or program name.  
Icon | An ICO file containing a set of frames sized 16x16, 32x32, 48x48, and 64x64 pixels, each with 8-bit and 32-bit color depth. This icon will appear in the main window of the client terminal, on the desktop, and in the Start menu. The icon file (terminal.ico) is also included in the directory of the installed terminal. Icons can be created using various free programs, such as [IcoFX](https://www.icofx.ro/) and others. A detailed guide on creating an icon using "Icon Studio" is available in the answer to the question: "[How to create an icon for the client terminal?"](https://support.metaquotes.net/en/articles/1460)  
  
In addition to these elements, the company name is also used in the installer. It is displayed in the window title, installation paths, and footers:

![Company name in the installer](images/wl_installer_company.png)

<a id="custom-files"></a>
### Custom files (#custom-files)

In this tab, you can upload files that will be automatically included in the client terminal build and placed into their respective folders.

Custom files should be taken from the corresponding folders of the client terminal. To prepare them, open the terminal, configure it as desired, close it, and then copy the necessary files. These can then be uploaded using the custom file upload interface. Do not include any files whose purpose you do not clearly understand. If you wish to keep all default settings and the appearance of the client terminal unchanged, you may skip this tab entirely.

Folder | File types  
---|---  
config | Here you can upload files that store terminal settings. Upon first launch after installation, the client terminal will apply these configurations. For example, terminal.ini stores data related to the position and size of the client terminal windows (note: this does not include chart windows, which are saved in the profile - see below). Keep in mind that the coordinates are stored in absolute values, which may result in different window positions on different screens. We do not recommend including this file in the terminal build. The file named trade.ini contains trading settings of the terminal (found under Tools - Options in the terminal menu). The common.ini file contains general settings (also under Tools - Options). It is strictly prohibited to upload a common.ini file that contains the value AllowDllImport=1. For security reasons, we do not allow DLL imports to be enabled by default for end users.  
bases\default\symbols | You can upload price history files here, along with a symbol set file that defines which instruments will appear in the Market Watch window on the terminal's first launch. For details please see "[How to change the default list of symbols in the client terminal label?](https://support.metaquotes.net/en/articles/1498)"  
MQL5 | This folder and its subfolders may contain custom indicators, scripts, or Expert Advisors (EAs) that will be available in the client terminal. It is strictly forbidden to include any .DLL files, or .EX5 files that reference external DLLs.  
MQL5\profiles\charts\default | Here, you can add a default terminal profile that will be applied on the first startup. For details please see "[How to change the default set of charts in the client terminal label?](https://support.metaquotes.net/en/articles/1499)"  
MQL5\profiles\symbolsets | This directory stores symbol set files (*.set) that can be selected from the context menu in the Market Watch window. You may create your own sets based on the types of instruments offered.  
MQL5\profiles\templates | You can upload your own chart templates (*.tpl) and terminal report templates (*.htm). You may also modify built-in report templates such as ReportTrade.htm, ReportHistory.htm, and ReportTester.htm, and upload the customized versions here.  
  
<a id="servers"></a>
### Servers (#servers)

In this tab, select the servers that should appear in the list when opening a new account in the terminal. Example:

![Broker's servers when opening an account from the client terminal](images/wl_servers_temrinal.png)

<a id="documents"></a>
### Documents (#documents)

Upload documents confirming the registration details of the company for which the White Label is being issued. A list of required documents can be found in the article "[Guide to easily meet KYC requirements](https://support.metaquotes.net/en/articles/1588)". Only color scans are accepted.

If you are editing an existing White Label and your company details have not changed, re-uploading the documents is not required.

<a id="submitting-the-final-version"></a>
### Submitting the final version (#submitting-the-final-version)

Carefully review all entered information before submitting the final version. After submission, changes can only be made once the client terminal build has been completed. To temporarily save your progress and return later, click "Save as a draft".

Once all data is confirmed, click "Send final version" in the bottom-right corner of the form.

<a id="what-happens-next"></a>
### What happens next (#what-happens-next)

After your order is confirmed (the automatically created ticket will change status to "Completed"), the client terminal White Label will be built using the information provided in the form. The download link for the [web installer](https://support.metaquotes.net/en/articles/427) will appear under [App Store / White Labels / MetaTrader 5](https://support.metaquotes.net/en/market/whitelabel/mt5).

To modify the White Label later, click the edit button in the block containing the desktop terminal link:

![Editing the White Label](images/white_label_edit.png)

> We strongly recommend that brokers use distribution links provided in the [App Store / White Labels / MetaTrader 5](https://support.metaquotes.net/en/market/whitelabel/mt5) section of this website when sharing installers with traders. If your corporate policy prohibits linking to external websites, you may host the files on your own server, just be sure to periodically check for and apply updates. Always keep your applications up to date!

<a id="platform-configuration-for-white-label"></a>
## Platform configuration for White Label (#platform-configuration-for-white-label)

Ensure that after the White Label is registered, your trading server receives the updated license file. By default, the trading server checks for license updates at the end of the trading day. To apply the update immediately, run a [manual platform update](../Platform-Setup/Live-Update.md). Note that this will restart your trading server.

If the server does not restart, it indicates an update error. Verify that the server machine can access: https://updates.metaquotes.net. For further details, check the [History server log](../Platform-Setup/Network-cluster/Journal.md) filtered by keyword "Update" or in the "logs\mt5srvupdater.log" file located in the [History server directory](../Platform-Components/History-Server/Structure-of-Directories-and-Files.md).

> If the license file is not updated, clients will see outdated company information in their terminals when connected to your server. Also, outdated data will be displayed in client statements.

<a id="mobile-terminal-wl"></a>
## White Label for the Mobile Terminal (#mobile-terminal-wl)

Mobile terminals allow your clients to manage their trading accounts without a desktop PC. Using smartphones, they can analyze market conditions and execute trades at any time.

Ordering a mobile terminal gives you access to several versions for different device types:

  * MetaTrader 5 for iPhone — for iPhone, iPod Touch and iPad powered by iOS 15.0 and higher;
  * MetaTrader 5 for Android — for smartphones and tablet PCs powered by Android OS 4.0 or higher.



Clients can connect to any trading server owned by a company that has purchased a mobile White Label.

To order the mobile terminal, select MetaTrader 5 Mobile in the [Buy section](https://support.metaquotes.net/en/market) of the technical support website. In the popup window, specify your company name. It must exactly match the name used in your desktop terminal's White Label.

Once the order is confirmed, a support ticket will be automatically created in the [Service Desk](https://support.metaquotes.net/en/servicedesk) with your order number in the title. This ticket will help you track the status of your order and provide any additional information if required. Once the order status changes to "Completed", the mobile White Label will be assembled for you.

The demo and live account opening settings configured in the [Account Allocation](../Platform-Setup/Accounts/Account-Allocation-Settings.md) section will be applied to the mobile terminal just like the desktop terminal. The server icon shown in the list will match the one used in the desktop terminal.

MetaTrader 5 for iPhone can be downloaded via [iTunes](https://download.mql5.com/cdn/mobile/mt5/ios?utm_campaign=support.metaquotes.net) or from the App Store on iPod Touch/iPhone/iPad. MetaTrader 5 for Android can be downloaded from the [Google Play](https://download.mql5.com/cdn/mobile/mt5/android?utm_campaign=support.metaquotes.net&hl=ru) website or Google Play mobile application.

Your server will be accessible for connecting both existing and new accounts.

![After you purchase the mobile White Label your server will be added to the available list of servers](images/wl_mobile.png)

By default, only the MetaQuotes-Demo server appears in the list. To find another server, users can simply type the first few letters of its name or the associated company. Server search results are filtered based on the account type - demo servers for demo accounts, real servers for real accounts.

If MetaTrader 5 mobile users encounter the error "invalid server name", it likely means that the [Company field in the group settings (#company)](../Platform-Setup/Groups/Group-Settings.md#company) is incorrect or does not match the company name associated with the mobile White Label.

![Connection error due to incorrect server name](images/wl_mobile_error.png)

You can always find the exact company name in the original White Label request ticket, on the [White Labels](https://support.metaquotes.net/en/market/whitelabel/mt5) page, or in the [edit form](https://support.metaquotes.net/en/forum/5854).

```

---
