# 📁 Development-Features

- **Generated:** 2026-09-09 00:09
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\Development-Features`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
Development-Features/
├── images/
│   ├── next.png
│   └── previous.png
└── README.md
```

---

## 📄 Files

<a id='readme-md'></a>
### 1. `README.md`

```markdown
[🏠 Document Start](../README.md) / Development Features

[Previous](../Tools/CMTFile/DirectoryClean.md) | [Next](../List-of-Events/README.md)

<a id="development-features"></a>
# Development Features (#development-features)

A number of important features of MetaTrader 5 API should be taken into account when developing applications. This will help to avoid many common issues.

<a id="volume"></a>
## Operations with Volumes (#volume)

MetaTrader 5 API supports two volume operation modes, implying standard and extended accuracy: 4 and 8 decimal places respectively. For that purpose, each structure and interface implying volumes provides pairs of members/methods. For example:

  * [IMTConfirm::Volume](../Database-Interfaces/Trade/Trade-Requests/IMTConfirm/Requests-Volume.md), [IMTExecution::DealVolume](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-DealVolume.md) — standard volume accuracy is used
  * [IMTConfirm::VolumeExt](../Database-Interfaces/Trade/Trade-Requests/IMTConfirm/Requests-VolumeExt.md), [IMTExecution::DealVolumeExt](../Database-Interfaces/Trade/Trade-Requests/IMTExecution/Requests-DealVolumeExt.md) — extended volume accuracy is used



All increased volume accuracy methods have names with the "Ext" addition. The standard mode is suitable for the most trading symbols. The extended accuracy mode is intended for cryptocurrencies.

In all methods which use standard accuracy, the volume is indicated as multiplied by 10,000. For example, 100 means 0.01 lots. In all extended accuracy methods, the volume is indicated as multiplied by 100,000,000. For example, 10,000,000 means 0.1 lot.

On the platform side, volume storage is not divided into two entities (normal and increased accuracy), the value is always stored in the INT64 format, with the fixed 8-digit accuracy. For example, IMTConfirm::Volume and IMTConfirm::VolumeExt methods read and set the same value on the platform side. If you set 1-lot volume using the IMTConfirm::Volume(10000) set-method, the same 1-lot volume will be obtained via the IMTConfirm::VolumeExt get-method, but it will be represented as a value of 100,000,000.

In structures (such as [MTTick](../Structures/MTTick.md)), the extended volume accuracy always has higher priority. When passing a structure in which both volume types are filled, the server will use the extended accuracy value. When returning volume values, the server fills both fields: with standard and extended accuracy.

> We strongly recommend not to mix methods utilizing different accuracy volumes within one project. If you switch to extended volume accuracy, make sure to convert the entire project to the extended accuracy rather than separate methods.

<a id="correspondence-of-software-interfaces-to-the-terminal-gui"></a>
## Correspondence of software interfaces to the terminal GUI (#correspondence-of-software-interfaces-to-the-terminal-gui)

The descriptions of the interfaces of configuration bases and database provide illustrations showing the correspondence of their methods to elements of the MetaTrader 5 Administrator and MetaTrader 5 Manager interface. The detailed descriptions of the platform functions are available in the References of appropriate terminals. The API documentation only provides a brief description of their nature and focuses mainly on programming features.

<a id="reserved-fields-in-structures"></a>
## Reserved Fields in Structures (#reserved-fields-in-structures)

Many structures used in MetaTrader 5 API contain reserved fields. It is not recommended to use these fields for your own needs. The trading platform developer may at any time remove or replace these fields.

<a id="resetting-structures"></a>
## Resetting Structures (#resetting-structures)

Before using structures, it is recommended to initialize them to zero. An example:
    
    
    MTTick tick={0};

<a id=""></a>
##  (#)

```

---
