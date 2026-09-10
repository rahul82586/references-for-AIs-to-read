#!/usr/bin/env python3
"""
Convert MT5 Manager REST swagger.json into a structured, offline-friendly Markdown
reference that can be used to develop endpoints.
"""
import json
import re
from pathlib import Path
from collections import defaultdict, OrderedDict

BASE = Path("/workspace/mtapi-docs")
SWAGGER = BASE / "swagger.json"
OUT_MD = BASE / "MT5-Manager-REST-API.md"


def load_spec():
    with SWAGGER.open() as f:
        return json.load(f)


def md_escape_inline(s):
    if s is None:
        return ""
    # escape pipe chars and newlines for tables
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def clean_desc(s):
    if not s:
        return ""
    s = str(s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</?[^>]+>", "", s)
    return s.strip()


def resolve_schema_ref(ref, components):
    if not ref or not ref.startswith("#/components/schemas/"):
        return None
    name = ref.rsplit("/", 1)[-1]
    return components.get("schemas", {}).get(name)


def render_schema_props(schema, components, depth=0, max_depth=6):
    if depth > max_depth or not isinstance(schema, dict):
        return ""
    if "$ref" in schema:
        target = resolve_schema_ref(schema["$ref"], components)
        if target is None:
            return ""
        return render_schema_props(target, components, depth + 1, max_depth)

    t = schema.get("type")
    out = []

    # enum-only schema
    if "enum" in schema:
        enums = ", ".join(str(e) for e in schema["enum"])
        out.append(f"**Enum:** `{enums}`")
        if schema.get("description"):
            out.append(clean_desc(schema["description"]))
        return "\n\n".join(x for x in out if x)

    if t == "object" or "properties" in schema:
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        if not props:
            return ""
        rows = ["| Field | Type | Required | Description |", "|---|---|---|---|"]
        for pname, pval in props.items():
            ptype, pdesc, pextras = describe_property(pval, components, depth + 1, max_depth)
            req = "yes" if pname in required else "no"
            rows.append(
                f"| `{md_escape_inline(pname)}` | `{md_escape_inline(ptype)}` | {req} | {md_escape_inline(pdesc)} |"
            )
        out.append("\n".join(rows))
        if pextras:
            out.append("\n".join(pextras))
        return "\n\n".join(x for x in out if x)

    # primitives
    return f"**Type:** `{t}`" + (
        f"\n\n{clean_desc(schema['description'])}" if schema.get("description") else ""
    )


def describe_property(pval, components, depth, max_depth):
    """Return (type_str, description, extras_list)."""
    desc = clean_desc(pval.get("description", "")) if isinstance(pval, dict) else ""
    extras = []

    if "$ref" in pval:
        ref_name = pval["$ref"].rsplit("/", 1)[-1]
        return (ref_name, desc, extras)

    t = pval.get("type")
    fmt = pval.get("format")
    if t == "array":
        items = pval.get("items", {})
        if "$ref" in items:
            inner = items["$ref"].rsplit("/", 1)[-1]
            return (f"array<{inner}>", desc, extras)
        return (f"array<{items.get('type','?')}>", desc, extras)
    if t == "object" and "properties" in pval:
        return ("object", desc, extras)
    type_str = t or "any"
    if fmt:
        type_str = f"{t}({fmt})"
    return (type_str, desc, extras)


def render_request_body(content, components):
    if not content:
        return ""
    parts = []
    for ctype, cval in content.items():
        schema = cval.get("schema", {})
        parts.append(f"**Content-Type:** `{ctype}`\n")
        sub = render_schema_props(schema, components)
        if sub:
            parts.append(sub)
        if "$ref" in schema:
            ref_name = schema["$ref"].rsplit("/", 1)[-1]
            parts.append(f"See schema: `{ref_name}`")
    return "\n\n".join(parts)


def render_responses(responses, components):
    if not responses:
        return ""
    rows = ["| Status | Description | Schema |", "|---|---|---|"]
    details = []
    for code, r in responses.items():
        desc = clean_desc(r.get("description", ""))
        schema = ""
        if "content" in r:
            for ctype, cval in r["content"].items():
                s = cval.get("schema", {})
                if "$ref" in s:
                    schema = s["$ref"].rsplit("/", 1)[-1]
                elif "type" in s:
                    schema = s.get("type", "")
                break
        rows.append(f"| `{code}` | {md_escape_inline(desc)} | {md_escape_inline(schema)} |")
        # if schema is a ref, render its full structure
        if "content" in r:
            for ctype, cval in r["content"].items():
                s = cval.get("schema", {})
                if "$ref" in s:
                    ref = s["$ref"].rsplit("/", 1)[-1]
                    target = resolve_schema_ref(s["$ref"], components)
                    if target:
                        sub = render_schema_props(target, components)
                        if sub:
                            details.append(f"**Response `{code}` schema — `{ref}`:**\n\n{sub}")
                break
    out = "\n".join(rows)
    if details:
        out += "\n\n" + "\n\n".join(details)
    return out


def render_parameters(params, components):
    if not params:
        return ""
    rows = ["| Name | In | Type | Required | Description |", "|---|---|---|---|---|"]
    for p in params:
        s = p.get("schema", {})
        ptype = ""
        if "$ref" in s:
            ptype = s["$ref"].rsplit("/", 1)[-1]
        elif s.get("type") == "array":
            inner = s.get("items", {})
            if "$ref" in inner:
                ptype = f"array<{inner['$ref'].rsplit('/',1)[-1]}>"
            else:
                ptype = f"array<{inner.get('type','?')}>"
        else:
            ptype = s.get("type", "")
            if s.get("format"):
                ptype = f"{s['type']}({s['format']})"
        rows.append(
            f"| `{md_escape_inline(p.get('name',''))}` | {p.get('in','')} | `{md_escape_inline(ptype)}` | "
            f"{'yes' if p.get('required') else 'no'} | {md_escape_inline(clean_desc(p.get('description','')))} |"
        )
    return "\n".join(rows)


def render_endpoint(path, method, op, components):
    lines = []
    lines.append(f"### `{method.upper()} {path}`")
    lines.append("")
    if op.get("summary"):
        lines.append(f"**Summary:** {clean_desc(op['summary'])}")
        lines.append("")
    if op.get("description"):
        lines.append(clean_desc(op["description"]))
        lines.append("")
    if op.get("operationId"):
        lines.append(f"`operationId: {op['operationId']}`")
        lines.append("")
    if op.get("deprecated"):
        lines.append("**DEPRECATED**")
        lines.append("")

    # params
    params = op.get("parameters", [])
    if params:
        lines.append("**Parameters**")
        lines.append("")
        lines.append(render_parameters(params, components))
        lines.append("")

    # request body
    rb = op.get("requestBody")
    if rb:
        lines.append("**Request Body**")
        lines.append("")
        lines.append(render_request_body(rb.get("content", {}), components))
        lines.append("")

    # responses
    if op.get("responses"):
        lines.append("**Responses**")
        lines.append("")
        lines.append(render_responses(op["responses"], components))
        lines.append("")

    # security
    if op.get("security"):
        sec = ", ".join(f"{list(s.keys())[0]}" for s in op["security"])
        lines.append(f"**Security:** {sec}")
        lines.append("")

    return "\n".join(lines)


def build_markdown():
    spec = load_spec()
    info = spec.get("info", {})
    components = spec.get("components", {})
    paths = spec.get("paths", {})
    tags = spec.get("tags", [])

    # group by tag
    grouped = defaultdict(list)
    for path, methods in paths.items():
        for method, op in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue
            tag_list = op.get("tags") or ["Untagged"]
            for t in tag_list:
                grouped[t].append((path, method, op))

    md = []
    md.append(f"# {info.get('title','MT5 Manager REST API')}")
    md.append("")
    md.append(f"**Version:** `{info.get('version','')}`")
    md.append("")
    if info.get("description"):
        md.append(clean_desc(info["description"]))
        md.append("")

    md.append("**Base URL:** `https://mng5.mtapi.io`  ")
    md.append("**Alternative demo:** `https://mt5mng.mtapi.io`  ")
    md.append("**OpenAPI Spec:** `https://mng5.mtapi.io/swagger/v1/swagger.json`")
    md.append("")
    md.append("---")
    md.append("")

    # Auth
    sec_schemes = components.get("securitySchemes", {})
    if sec_schemes:
        md.append("## Authentication")
        md.append("")
        for name, sch in sec_schemes.items():
            md.append(f"### `{name}` — {sch.get('type','')}")
            md.append("")
            if sch.get("description"):
                md.append(clean_desc(sch["description"]))
                md.append("")
            if sch.get("in"):
                md.append(f"- **In:** `{sch['in']}`")
            if sch.get("name"):
                md.append(f"- **Name:** `{sch['name']}`")
            md.append("")
        md.append("---")
        md.append("")

    # TOC
    md.append("## Table of Contents")
    md.append("")
    md.append("### Endpoint Sections")
    for t in tags:
        tname = t.get("name", t) if isinstance(t, dict) else t
        slug = re.sub(r"[^a-z0-9]+", "-", str(tname).lower()).strip("-")
        md.append(f"- [{tname}](#{slug})  ({len(grouped.get(tname, []))} endpoints)")
    md.append(f"- [Schemas](#schemas)  ({len(components.get('schemas', {}))} models)")
    md.append("")
    md.append("---")
    md.append("")

    # Endpoints grouped by tag, in the order tags appear in the spec
    ordered_tag_names = [t.get("name", t) if isinstance(t, dict) else t for t in tags]
    seen = set()
    for tname in ordered_tag_names:
        eps = grouped.get(tname, [])
        if not eps:
            continue
        seen.add(tname)
        md.append(f"## {tname}")
        md.append("")
        md.append(f"_{len(eps)} endpoint(s)_")
        md.append("")
        for path, method, op in eps:
            md.append(render_endpoint(path, method, op, components))
        md.append("---")
        md.append("")
    # any untagged / extra groups
    for tname, eps in grouped.items():
        if tname in seen:
            continue
        md.append(f"## {tname}")
        md.append("")
        for path, method, op in eps:
            md.append(render_endpoint(path, method, op, components))
        md.append("---")
        md.append("")

    # Schemas
    md.append("## Schemas")
    md.append("")
    md.append(f"_{len(components.get('schemas', {}))} data models_")
    md.append("")
    md.append("Each schema below corresponds to a `components.schemas.<Name>` entry in the OpenAPI spec. Endpoints reference these models in their request/response bodies.")
    md.append("")

    schemas = components.get("schemas", {})
    # sort by name, but keep "main" / "core" objects first
    important_keywords = ("Account", "Order", "Deal", "Position", "User", "Symbol", "Quote", "Tick", "Group", "Con", "MT")
    def sort_key(name):
        for i, kw in enumerate(important_keywords):
            if name.startswith(kw):
                return (i, name)
        return (99, name)
    sorted_names = sorted(schemas.keys(), key=sort_key)

    for name in sorted_names:
        s = schemas[name]
        md.append(f"### `{name}`")
        md.append("")
        if s.get("description"):
            md.append(clean_desc(s["description"]))
            md.append("")
        # enum
        if "enum" in s:
            md.append("**Allowed values:**")
            md.append("")
            for e in s["enum"]:
                md.append(f"- `{e}`")
            md.append("")
            continue
        body = render_schema_props(s, components)
        if body:
            md.append(body)
            md.append("")
        # also dump required fields list explicitly
        req = s.get("required", [])
        if req:
            md.append(f"**Required fields:** {', '.join(f'`{r}`' for r in req)}")
            md.append("")
        md.append("---")
        md.append("")

    # Servers
    if spec.get("servers"):
        md.append("## Servers")
        md.append("")
        for s in spec["servers"]:
            md.append(f"- `{s.get('url','')}`  {clean_desc(s.get('description',''))}")
        md.append("")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_MD}  ({OUT_MD.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build_markdown()
