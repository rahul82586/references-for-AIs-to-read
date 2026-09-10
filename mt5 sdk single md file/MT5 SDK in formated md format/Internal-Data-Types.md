# 📁 Internal-Data-Types

- **Generated:** 2026-09-09 00:10
- **Total Files:** 1
- **Source:** `C:\Users\DELL\Downloads\server3\mt5_doc_dump\Documentation\MQ_Docs\Metatrader 5\MetaTrader5SDK\Internal-Data-Types`

---

## 📑 Table of Contents

1. [README.md](#readme-md)

---

## 🌲 Project Structure

```
Internal-Data-Types/
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
[🏠 Document Start](../README.md) / Internal Data Types

[Previous](../SQL-Export/Installation-and-Setup-of-PostgreSQL.md) | [Next](../Journal-Constants/README.md)

<a id="internal-data-types"></a>
# Internal Data Types (#internal-data-types)

Fur the purpose of convenience, MetaTrader 5 API has its own data types.

<a id="mtapires"></a>
## MTAPIRES (#mtapires)

The internal data type MTAPIRES is designed for returning [response codes](../Return-Codes/README.md) of the server. MTAPIRES is a value of the UINT type.

<a id="mtapistr"></a>
## MTAPISTR (#mtapistr)

MTAPISTR is a data type used for returning strings of a fixed length. This type is an array of values wchar_t type. The string length is limited to 260 characters (including the sign of the string end).

<a id="mtsortfunctionptr"></a>
## MTSortFunctionPtr (#mtsortfunctionptr)

This type is used in the functions of object sorting and search in dynamic arrays. It is a pointer to the function of comparison of two values, to which *left and *right point. It is similar to the CRT-functions of sorting "qsort" and "bsearch".
    
    
    typedef int (__cdecl *MTSortFunctionPtr)(const void *left, const void *right);

Depending on the comparison results, the following values are returned:

  * <0 — if left is less than right;
  * 0 — if left is equal to right;
  * >0 — if left is greater than right.



It is used in the search methods of interfaces for working with arrays. For example:

  * [IMTOrderArray](../Database-Interfaces/Trade/Orders/IMTOrderArray.md)
  * [IMTDealArray](../Database-Interfaces/Trade/Deals/IMTDealArray.md)
  * [IMTPositionArray](../Database-Interfaces/Trade/Positions/IMTPositionArray.md)



```

---
