# -*- coding: utf-8 -*-
import shutil, sys

SRC = "codigo html evento acceso.txt"
DST = "dashboard_noc_mejorado.html"

html = open(SRC, encoding="utf-8").read()
original = html

def patch(old, new, desc):
    global html
    n = html.count(old)
    assert n == 1, f"[FALLO] '{desc}': se esperaba 1 ocurrencia, hay {n}"
    html = html.replace(old, new)
    print(f"[OK] {desc}")

# ---------- 1) Bug: Disponibilidad 0.000% ----------
patch("100-H/(n*24)*100",
      "100-(H/Math.max(1,S))/(n*24)*100",
      "Disponibilidad promedio por evento")

# ---------- 2) Bug: +1100% vs histórico ----------
patch("(S-tE/12)/(tE/12)*100",
      "(S-tE)/Math.max(1,tE)*100",
      "Variación filtrado vs base real")

# ---------- 3) Robustez carga Excel ----------
patch("cC=(S)=>{if(!S)return;let H=new FileReader;H.onload=",
      "cC=(S)=>{if(!S)return;if(typeof window.XLSX===\"undefined\")"
      "{window.alert(\"No se pudo cargar la librería XLSX. Revisa tu conexión a internet.\");return}"
      "let H=new FileReader;H.onerror=()=>window.alert(\"No se pudo leer el archivo seleccionado.\");H.onload=",
      "Manejo de errores en carga de Excel")

# ---------- 4) Documento válido (el archivo empieza directo en <body>) ----------
HEAD = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gestión de Eventos Acceso - NOC</title>
<meta name="description" content="Dashboard operativo NOC: eventos de acceso, KPIs, filtros por año/mes/semana/causa/región y exportación de datos.">
<meta name="theme-color" content="#0e1120">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23f5b800'/%3E%3Ctext x='32' y='45' font-size='36' font-weight='900' text-anchor='middle' font-family='Arial,sans-serif' fill='%23000'%3EN%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
  /* Rendimiento: renderizado diferido de cards fuera de pantalla */
  .card{content-visibility:auto;contain-intrinsic-size:220px;}
  /* Accesibilidad: indicador de foco visible */
  .select-dark:focus-visible,button:focus-visible{outline:2px solid #f5b800;outline-offset:2px;}
  /* Modo impresión */
  @media print{
    body{background:#fff !important;}
    header{position:static !important;}
    header button,.select-dark,.border-dashed{display:none !important;}
    .card{break-inside:avoid;border-color:#d5d5d5 !important;background:#fff !important;}
    .card *{color:#111 !important;}
  }
</style>
</head>
<body>'''

assert html.lstrip().startswith("<body>"), "El archivo no empieza con <body>"
html = HEAD + html[html.index("<body>") + len("<body>"):].replace("\n  \n\n</body>", "\n\nMEJORAS_AQUI\n</body>", 1)
print("[OK] Estructura HTML5 + head completo")

# ---------- 5) Capa de mejoras externa (accesibilidad, teclado, errores) ----------
MEJORAS = '''
<script>
(function(){
  "use strict";

  /* ---- Accesibilidad: labels, landmarks y tabs ---- */
  function enhance(){
    var root = document.getElementById("root");
    var app  = root && root.firstElementChild;
    if(!app) return;
    app.setAttribute("role","main");
    var header = app.querySelector("header");
    if(header) header.setAttribute("role","banner");

    var labelsFiltro = ["Filtrar por año","Filtrar por mes","Filtrar por semana","Filtrar por causa","Filtrar por región"];
    app.querySelectorAll("select.select-dark").forEach(function(s,i){
      s.setAttribute("aria-label", labelsFiltro[i] || "Filtro");
    });

    var btns = app.querySelectorAll("header button");
    if(btns[0]) btns[0].setAttribute("aria-label","Cargar archivo Excel (.xlsx)");
    if(btns[1]) btns[1].setAttribute("aria-label","Exportar datos filtrados a Excel");
    if(btns[2]) btns[2].setAttribute("aria-label","Limpiar todos los filtros");

    /* Tabs: roles + navegación con teclado */
    var tabs = Array.prototype.slice.call(app.querySelectorAll(".overflow-x-auto > div > button"));
    if(!tabs.length) return;
    var list = tabs[0].parentElement;
    list.setAttribute("role","tablist");
    function sync(){
      tabs.forEach(function(t){
        var activa = !!t.querySelector(".bg-\\[\\#f5b800\\]") ||
                     !!(t.nextElementSibling === null && false);
        var activaReal = t.querySelector("span.bg-\\[\\#f5b800\\]");
        t.setAttribute("role","tab");
        t.setAttribute("aria-selected", activaReal ? "true" : "false");
        t.setAttribute("tabindex", activaReal ? "0" : "-1");
      });
    }
    sync();
    tabs.forEach(function(t,i){
      t.addEventListener("click", function(){ setTimeout(sync,0); });
      t.addEventListener("keydown", function(e){
        var k = e.key, n = null;
        if(k==="ArrowRight") n = (i+1) % tabs.length;
        else if(k==="ArrowLeft") n = (i-1+tabs.length) % tabs.length;
        else if(k==="Home") n = 0;
        else if(k==="End") n = tabs.length-1;
        if(n===null) return;
        e.preventDefault();
        tabs[n].focus(); tabs[n].click(); sync();
      });
    });
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",enhance);
  else enhance();

  /* ---- Resiliencia: toast global de errores ---- */
  function toast(msg, color){
    var t = document.createElement("div");
    t.textContent = msg;
    t.style.cssText = "position:fixed;bottom:18px;right:18px;z-index:9999;max-width:360px;"
      + "padding:12px 16px;border-radius:12px;font:600 13px system-ui,sans-serif;color:" + (color||"#f5b800")
      + ";background:#1a1f38;border:1px solid " + (color||"#f5b800") + ";box-shadow:0 8px 30px rgba(0,0,0,.5);";
    document.body.appendChild(t);
    setTimeout(function(){ t.style.opacity="0"; t.style.transition="opacity .4s"; }, 4500);
    setTimeout(function(){ t.remove(); }, 5000);
  }
  window.addEventListener("error", function(e){
    if(e && e.message) toast("Error en la aplicación: " + e.message, "#ef4444");
  });
})();
</script>
'''
html = html.replace("MEJORAS_AQUI", MEJORAS)
print("[OK] Capa de accesibilidad / teclado / errores")

assert html != original, "Sin cambios"
open(DST, "w", encoding="utf-8").write(html)
print(f"\n✔ Generado: {DST} ({len(html):,} bytes)")
