import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { UploadCloud, Save, PlusCircle, CheckCircle2 } from "lucide-react";
import * as YAML from "yaml";

/**
 * GUI‑Tool zum halb‑automatischen Erstellen von Analyse‑Schemata
 * --------------------------------------------------------------
 * Features
 * 1. Marker‑Dateien (YAML | JSON) laden
 * 2. Marker filtern & Gewichte/Attribute bearbeiten
 * 3. JSON‑Schema live zusammenstellen & validieren (Stub)
 * 4. Export als Datei
 */
export default function SchemaBuilderApp() {
  const [rawFile, setRawFile] = useState("");
  const [markers, setMarkers] = useState([]); // flache Liste aller Marker‐Objs
  const [filter, setFilter] = useState("");
  const [schemaJson, setSchemaJson] = useState({});
  const [validation, setValidation] = useState({ ok: true, messages: [] });

  // ---------- Datei laden & Marker parsen ----------
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const txt = evt.target.result;
      setRawFile(txt);
      try {
        const data = file.name.endsWith(".yaml") || file.name.endsWith(".yml") ? YAML.parse(txt) : JSON.parse(txt);
        const flatMarkers = Array.isArray(data) ? data : data.markers ?? [];
        setMarkers(flatMarkers);
      } catch (err) {
        console.error("Parse‑Fehler", err);
        alert("⚠️ Datei konnte nicht geparst werden. Prüfe Format.");
      }
    };
    reader.readAsText(file, "utf‑8");
  };

  // ---------- Marker‑Gewicht ändern ----------
  const updateWeight = (idx, newWeight) => {
    setMarkers((prev) => {
      const copy = [...prev];
      copy[idx] = { ...copy[idx], scoring: { ...(copy[idx].scoring || {}), weight: Number(newWeight) } };
      return copy;
    });
  };

  // ---------- Schema bauen ----------
  const buildSchema = () => {
    const groups = markers.reduce((acc, m) => {
      const lvl = m.level || "atomic";
      acc[lvl] = acc[lvl] || [];
      acc[lvl].push({ id: m.id, count: 0 });
      return acc;
    }, {});
    const json = {
      meta: { created: new Date().toISOString(), marker_source: "upload" },
      groups,
      outputs: {
        overall_risk_score: 0,
        risk_level: "green",
      },
    };
    setSchemaJson(json);
  };

  // ---------- Dummy‑Validierung ----------
  const validateSchema = () => {
    const msgs = [];
    if (!schemaJson.groups || Object.keys(schemaJson.groups).length === 0) msgs.push("Keine Gruppen definiert.");
    markers.forEach((m) => {
      if (!m.scoring?.weight) msgs.push(`Marker ${m.id} hat kein Gewicht.`);
    });
    setValidation({ ok: msgs.length === 0, messages: msgs });
  };

  // ---------- Export ----------
  const exportJson = () => {
    const blob = new Blob([JSON.stringify(schemaJson, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analysis_schema_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filtered = markers.filter((m) => m.id?.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="p-4 grid gap-4 lg:grid-cols-3">
      {/* Sidebar */}
      <Card className="lg:col-span-1 h-full">
        <CardHeader className="flex flex-row items-center justify-between">
          <h2 className="text-xl font-semibold">Marker‑Quelle</h2>
          <label className="cursor-pointer hover:opacity-80">
            <UploadCloud className="w-5 h-5" />
            <Input type="file" accept=".json,.yaml,.yml" onChange={handleFileUpload} className="hidden" />
          </label>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Input placeholder="Marker filtern…" value={filter} onChange={(e) => setFilter(e.target.value)} />
          <div className="h-[55vh] overflow-auto space-y-2 pr-2">
            {filtered.map((m, idx) => (
              <div key={m.id} className="flex items-center justify-between bg-muted p-2 rounded-xl">
                <span className="truncate text-sm" title={m.description}>{m.id}</span>
                <input
                  type="number"
                  step="0.1"
                  className="w-16 bg-transparent text-right"
                  value={m.scoring?.weight ?? ""}
                  onChange={(e) => updateWeight(idx, e.target.value)}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Builder */}
      <Card className="lg:col-span-2 h-full">
        <CardHeader className="flex flex-row items-center justify-between">
          <h2 className="text-xl font-semibold">Schema‑Builder</h2>
          <div className="flex gap-2">
            <Button variant="secondary" className="flex gap-1" onClick={buildSchema}>
              <PlusCircle className="w-4 h-4" /> Schema erstellen
            </Button>
            <Button variant="secondary" className="flex gap-1" onClick={validateSchema}>
              <CheckCircle2 className="w-4 h-4" /> Validieren
            </Button>
            <Button variant="default" className="flex gap-1" onClick={exportJson} disabled={!schemaJson.groups}>
              <Save className="w-4 h-4" /> Export
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {validation.messages.length > 0 && (
            <div className={`p-3 rounded-xl ${validation.ok ? "bg-emerald-100" : "bg-red-100"}`}>
              {validation.messages.map((msg) => (
                <p key={msg} className="text-sm">{msg}</p>
              ))}
            </div>
          )}
          <Textarea
            readOnly
            className="h-[55vh] font-mono text-xs"
            value={schemaJson && Object.keys(schemaJson).length ? JSON.stringify(schemaJson, null, 2) : "// Hier erscheint dein Schema"}
          />
        </CardContent>
      </Card>
    </div>
  );
}
