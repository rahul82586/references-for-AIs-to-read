# 📁 SQL-Export

- **Generated:** 2026-09-09 00:12
- **Total Files:** 7
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\SQL-Export`

---

## 📑 Table of Contents

1. [Installation-and-Setup-of-FireBird.md](#installation-and-setup-of-firebird-md)
2. [Installation-and-Setup-of-MS-SQL.md](#installation-and-setup-of-ms-sql-md)
3. [Installation-and-Setup-of-MariaDB.md](#installation-and-setup-of-mariadb-md)
4. [Installation-and-Setup-of-MySQL.md](#installation-and-setup-of-mysql-md)
5. [Installation-and-Setup-of-Oracle.md](#installation-and-setup-of-oracle-md)
6. [Installation-and-Setup-of-PostgreSQL.md](#installation-and-setup-of-postgresql-md)
7. [README.md](#readme-md)

---

## 🌲 Project Structure

```
SQL-Export/
├── images/
│   ├── fb_setting_local.png
│   ├── fb_setting_remote.png
│   ├── firebird_base_create.png
│   ├── firebird_install.gif
│   ├── firebird_install2.gif
│   ├── mariadb_create_db.png
│   ├── mariadb_install.gif
│   ├── mariadb_install2.gif
│   ├── mariadb_setting_local.png
│   ├── mariadb_setting_remote.png
│   ├── mssql_6_a.png
│   ├── mssql_8_a.png
│   ├── mssql_aa.png
│   ├── mssql_ba.png
│   ├── mssql_tcp.png
│   ├── mysql_configure.gif
│   ├── mysql_configure_finish.gif
│   ├── mysql_configure_users.png
│   ├── mysql_install.gif
│   ├── mysql_platform_local.png
│   ├── mysql_platform_remote.png
│   ├── next.png
│   ├── next_1.png
│   ├── next_2.png
│   ├── next_3.png
│   ├── next_4.png
│   ├── next_5.png
│   ├── next_6.png
│   ├── oracle_4.png
│   ├── oracle_setting_local.png
│   ├── oracle_setting_remote.png
│   ├── postgre1.gif
│   ├── postgre2.gif
│   ├── postgre3.gif
│   ├── postgre_db_create.png
│   ├── postgres_settings_local.png
│   ├── postgres_settings_remote.png
│   ├── previous.png
│   ├── previous_1.png
│   ├── previous_2.png
│   ├── previous_3.png
│   ├── previous_4.png
│   ├── previous_5.png
│   └── previous_6.png
├── Installation-and-Setup-of-FireBird.md
├── Installation-and-Setup-of-MariaDB.md
├── Installation-and-Setup-of-MS-SQL.md
├── Installation-and-Setup-of-MySQL.md
├── Installation-and-Setup-of-Oracle.md
├── Installation-and-Setup-of-PostgreSQL.md
└── README.md
```

---

## 📄 Files

<a id='installation-and-setup-of-firebird-md'></a>
### 7. `Installation-and-Setup-of-FireBird.md`

```markdown
[🏠 Document Start](../README.md) / [SQL Export](README.md) / Installation and Setup of FireBird

[Previous](Installation-and-Setup-of-MariaDB.md) | [Next](Installation-and-Setup-of-MS-SQL.md)

# Installation and Setup of FireBird

Download one of the distribution kits from FireBird website ([http://www.firebirdsql.org/en/server-packages](https://www.firebirdsql.org/en/server-packages)).

> Select 32 or 64-bit considering potential volumes of databases. 64-bit server version is more preferable, as it makes possible to have data caches of more than 2 GB and has better scalability due to increasing RAM on the server.

Run the installation file and follow the on-screen instructions. Agree to the terms of use and specify FireBird installation path (you may use the default path). Next, specify the list of components to install or use the default option.

![FireBird installation](images/firebird_install.gif)

Then specify the name for the program group in the Start menu and configure the integration of the FireBird server with the operating system (these parameters can also be left by default). At the next step, specify the password for the SYSDBA login (administrator account). Start the installation process by pressing "Install" and wait for it to finish.

![FireBird installation](images/firebird_install2.gif)

After installation, you need to create a schema (database) to which data will be exported. To do this, open "Start — All Programs — FireBird 3.0" and launch "Firebird ISQL Tool". Execute the following command in it:

CREATE DATABASE 'path_to_the_DB\DB-file_name.fdb' page_size 16384 user 'user_name' password 'password';  
---  
  
Example:

![Example of FireBird database creation](images/firebird_base_create.png)

In this example, 'c:\databases' directory should be created in advance.

Additional Firebird setup should be performed to increase efficiency. To do this, edit the firebird.conf configuration text file in the installation directory:

# ----------------------------  
# Number of cached database pages  
#  
# This sets the number of pages from any one database that can be held  
# in cache at once. If you increase this value, the engine will  
# allocate more pages to the cache for every database. By default, the  
# SuperServer allocates 2048 pages for each database and the classic  
# allocates 75 pages per client connection per database.  
#  
# Type: integer  
#  
  
DefaultDbCachePages = 65536  
---  
  
It means that DefaultDbCachePages line should be uncommented and the value of 65536 should be set for it. This will make Firebird to use cache of 1 GB for the database. If necessary, you can set a lower value using the following equation:

Cache size = Page size (16 Kb) * DefaultDbCachePages  
---  
  
> The maximum value for DefaultDbCachePages is 65536 meaning that the maximum cache for 16 Kb pages will be approximately equal to 1 GB.

In case backup and FireBird servers are installed on the same computer, connection settings will be as follows:

![fb_setting_local](images/fb_setting_local.png)

In case backup and FireBird servers are located on different computers:

![fb_setting_remote](images/fb_setting_remote.png)

> It is recommended to install FireBird and backup servers on the same computer for faster export. It should also be kept in mind that the backup server itself also consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backups will work close to necessary DBMS.

Additional export parameters can be selected at [SQL Options (#sql-settings)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_network/network_add_edit/network_backup_server#sql-settings) tab.

The backup server will immediately start export into the external DBMS after all settings are specified. Request the log of the appropriate backup server using SQL keyword to track the export process: 

2012.10.17 15:16:08 SQL Export Firebird: successfully connected to database 'c:\databases\metatrader5.fdb' at '127.0.0.1' as user 'SYSDBA'  
2012.10.17 15:16:08 SQL Export Firebird: server version 3.0.2  
2012.10.17 15:16:08 SQL Export Firebird: table 'mt5_symbols' creating started  
2012.10.17 15:16:08 SQL Export Firebird: table 'mt5_symbols' created  
2012.10.17 15:16:08 SQL Export Firebird: primary key for 'mt5_symbols' adding started  
2012.10.17 15:16:08 SQL Export Firebird: primary key for 'mt5_symbols' added  
2012.10.17 15:16:08 SQL Export Firebird: table 'mt5_symbols_sessions' creating started  
2012.10.17 15:16:08 SQL Export Firebird: table 'mt5_symbols_sessions' created  
2012.10.17 15:16:08 SQL Export Firebird: primary key for 'mt5_symbols_sessions' adding started  
2012.10.17 15:16:08 SQL Export Firebird: primary key for 'mt5_symbols_sessions' added  
2012.10.17 15:16:08 SQL Export Symbols: 0 symbols and 0 sessions loaded in 93 msecs  
2012.10.17 15:16:08 SQL Export Symbols: synchronization started  
...  
---

```

---

<a id='installation-and-setup-of-ms-sql-md'></a>
### 7. `Installation-and-Setup-of-MS-SQL.md`

```markdown
[🏠 Document Start](../README.md) / [SQL Export](README.md) / Installation and Setup of MS SQL

[Previous](Installation-and-Setup-of-FireBird.md) | [Next](Installation-and-Setup-of-Oracle.md)

# Installation and Setup of Microsoft SQL Server

Download one of the distribution kits from Microsoft website ([http://www.microsoft.com/en-us/download/details.aspx?id=29062](https://www.microsoft.com/en-us/download/details.aspx?id=29062)) to install free version of Microsoft SQL Exress 2012.

You need to download ENU\x86\SQLEXPR_x86_ENU.exe or ENU\x64\SQLEXPR_x64_ENU.exe.

  * MetaTrader 5 supports data export both to Microsoft SQL Server 2005/2008/2012/2014/2016 and to their Express versions.
  * Microsoft SQL Server Express 2005 has a limit of 4 GB on user data. Microsoft SQL Server Express 2008 R2 / 2012 has a limit of 10 GB. Therefore, it is recommended to use 2008 R2 or 2012 as Express version. If the limit is exceeded, new data will not be added to the database.


  * Operating system Windows 8 or higher is required for the [Microsoft SQL 2016](https://www.microsoft.com/en-us/download/details.aspx?id=54284) installation.


  * Select 32 or 64-bit considering potential volumes of databases. 64-bit server version is more preferable, as it makes possible to have data caches of bigger volume and has better scalability due to increasing RAM on the server.

  
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

Additional export parameters can be selected at [SQL Options (#sql-settings)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_network/network_add_edit/network_backup_server#sql-settings) tab.

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

<a id='installation-and-setup-of-mariadb-md'></a>
### 7. `Installation-and-Setup-of-MariaDB.md`

```markdown
[🏠 Document Start](../README.md) / [SQL Export](README.md) / Installation and Setup of MariaDB

[Previous](Installation-and-Setup-of-MySQL.md) | [Next](Installation-and-Setup-of-FireBird.md)

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

Additional export parameters can be selected at [SQL Options (#sql-settings)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_network/network_add_edit/network_backup_server#sql-settings) tab.

```

---

<a id='installation-and-setup-of-mysql-md'></a>
### 7. `Installation-and-Setup-of-MySQL.md`

```markdown
[🏠 Document Start](../README.md) / [SQL Export](README.md) / Installation and Setup of MySQL

[Previous](README.md) | [Next](Installation-and-Setup-of-MariaDB.md)

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
  
In case backup and MySQL servers are installed on the same computer, connection settings will be as follows:

![Export settings when installing MySQL on the same computer where the backup server is installed](images/mysql_platform_local.png)

In case backup and MySQL servers are located on different computers:

![Export settings when installing MySQL on a separate computer](images/mysql_platform_remote.png)

> It is recommended to install MySQL and backup servers on the same computer for faster export. It should also be kept in mind that the backup server itself also consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backups will work close to necessary DBMS.

Additional export parameters can be selected at [SQL Options (#sql-settings)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_network/network_add_edit/network_backup_server#sql-settings) tab.

After all settings are specified, the backup server will immediately start export into the external DBMS. Request the log of the appropriate backup server using SQL keyword to track the export process:

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

<a id='installation-and-setup-of-oracle-md'></a>
### 7. `Installation-and-Setup-of-Oracle.md`

```markdown
[🏠 Document Start](../README.md) / [SQL Export](README.md) / Installation and Setup of Oracle

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
  
Additional export parameters can be selected at [SQL Options (#sql-settings)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_network/network_add_edit/network_backup_server#sql-settings) tab.

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

<a id='installation-and-setup-of-postgresql-md'></a>
### 7. `Installation-and-Setup-of-PostgreSQL.md`

```markdown
[🏠 Document Start](../README.md) / [SQL Export](README.md) / Installation and Setup of PostgreSQL

[Previous](Installation-and-Setup-of-Oracle.md) | [Next](../Internal-Data-Types/README.md)

# Installation and Setup of PostgreSQL

Download the required version of PostgreSQL installer from the [official website](https://www.postgresql.org/download/).

> ["Update for Visual C++ 2013 and Visual C++ Redistributable Package"](https://support.microsoft.com/en-us/help/3179560/update-for-visual-c-2013-and-visual-c-redistributable-package) must be installed on the computer where the backup server is installer. Otherwise expert to Oracle databases will not be possible.

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

> It is recommended to install PostgreSQL and the backup server on the same computer for faster export. However, it should also be kept in mind that the backup server consumes resources. Also, remember that it is possible to deploy several backups for a trade server. These backup servers will run close to necessary DBMS. 

Additional export parameters can be selected at [SQL Options (#sql-settings)](https://support.metaquotes.net/en/docs/mt5/platform/administration/admin_network/network_add_edit/network_backup_server#sql-settings) tab.

The backup server will immediately start export into the external DBMS after all settings are specified. Request the log of the appropriate backup server using SQL keyword to track the export process:

2017.12.21 15:17:17.154 SQL Export PostgreSQL: server version 10.1   
2017.12.21 15:17:17.156 SQL Export PostgreSQL: successfully connected to database 'metatrader5' at 'localhost' as user 'postgres'   
2017.12.21 15:17:17.170 SQL Export PostgreSQL: table 'mt5_symbols_sessions' creating started   
2017.12.21 15:17:17.180 SQL Export PostgreSQL: table 'mt5_symbols_sessions' created   
...  
---

```

---

<a id='readme-md'></a>
### 7. `README.md`

```markdown
[🏠 Document Start](../README.md) / SQL Export

[Previous](../Web-API/Manager-Interface-(Rest-API)/NET-Implementation-of-Protocol/WebTrader.md) | [Next](Installation-and-Setup-of-MySQL.md)

# SQL Export

The MetaTrader 5 trading platform provides standard options for the real-time data export to MySQL, Microsoft SQL Server, FireBird, Oracle, MariaDB and PostgreSQL databases. This option enables the quick and easy deployment of data export to an external DBMS for using the platform data in any popular programming language and third-party applications. Thus, it is possible to create an intermediate layer between a trade server and broker's program services that regularly access trading data. This reduces the load on the trade server when it receives the current trading data.

The export function is enabled by simple specification of settings for connection to DBMS via MetaTrader 5 Administrator. After that, the backup server will immediately perform an initial synchronization of data from the DBMS. Further, new data will be exported to the DBMS in real time. The following data is exported:

  * Information about clients (general information and trading status)
  * Current active orders and positions
  * The history of orders and deals
  * Current prices
  * Virtually all settings of the trading platform (except for the working time, synchronization and spreads)



The description of installation and setup of popular databases is provided in appropriate subsections:

  * [MySQL Server 5.7](Installation-and-Setup-of-MySQL.md) (supported versions: 5.1, 5.5, 5.6, 5.7)
  * [MariaDB 10.2](Installation-and-Setup-of-MariaDB.md) (all version supported)
  * [FireBird 3.0](Installation-and-Setup-of-FireBird.md) (supported versions: 2.0, 2.1, 2.5, 3.0)
  * [Microsoft SQL Express 2012](Installation-and-Setup-of-MS-SQL.md) (supported versions: 2005, 2008, 2008 R2, 2012, 2014, 2016)
  * [Oracle Database Express Edition 11g](Installation-and-Setup-of-Oracle.md) (supported versions: 11g/11g Express Edition, 12c)
  * [PostgreSQL](Installation-and-Setup-of-PostgreSQL.md) (supported versions: 8.4 — 10.1)



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

A detailed description of exported tables can be found in the [MetaTrader 5 Administrator User Guide](https://support.metaquotes.net/en/docs/mt5/platform/components/backup_server/sql_export).

## Your own data in MetaTrader 5 tables

In the platform, you can create your own tables and databases, add your own fields in mt5_* tables, which are used for data export, as well as create stored procedures and triggers.

  * The backup server does not recreate data, but only adds or updates existing records. A table entry is only deleted if the appropriate entry is deleted on the platform side. For example, if a user is added to the mt5_users tables, the appropriate user record will exist in the database until the user is deleted from MetaTrader 5.
  * The backup server only works with its own tables and fields.
  * The backup server does not create default indexes. Each index is an extra load on the database, which can slow down exports and information updates.
  * When you create your own fields in mt5_* tables, do not forget to set default values for them (or allow NULL). Otherwise, the backup server will not be able to add new entries to the tables.



```

---
