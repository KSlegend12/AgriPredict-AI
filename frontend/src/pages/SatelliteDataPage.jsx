import React from 'react';
import { CheckCircle2, Clock3, Database, Droplets, Leaf, Satellite, Thermometer, Waves } from 'lucide-react';

const datasets = [
  { name: 'MOD13Q1.061', period: '2017–2024', features: 'NDVI · EVI', status: 'Complete', icon: Leaf, color: 'emerald' },
  { name: 'MOD16A2GF.061', period: '2017–2024', features: 'ET · PET', status: 'Complete', icon: Waves, color: 'sky' },
  { name: 'MOD17A2HGF.061', period: '2017–2024', features: 'GPP · PSN', status: 'Complete', icon: Leaf, color: 'violet' },
  { name: 'MOD11A2.061', period: '2017–2024', features: 'LST Day · LST Night', status: 'Complete', icon: Thermometer, color: 'amber' },
  { name: 'SMAP SPL4SMGP.008', period: '2015–2024', features: 'Surface · Root-zone soil moisture', status: 'Processing', icon: Droplets, color: 'cyan' },
  { name: 'MOD15A2H.061', period: '2017–2024', features: 'LAI · FPAR', status: 'Processing', icon: Leaf, color: 'lime' },
];

export default function SatelliteDataPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-slate-950 p-7 sm:p-9 text-white"><div className="inline-flex items-center gap-2 rounded-full bg-cyan-400/10 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-cyan-300"><Satellite className="h-3.5 w-3.5" /> Multi-source Earth observation</div><h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">Satellite Data Pipeline</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">The project is evaluating complementary satellite signals for vegetation condition, productivity, water use, heat stress and soil moisture. Dataset quality is tested before any production integration.</p></section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {datasets.map((d) => <DatasetCard key={d.name} {...d} />)}
      </section>

      <section className="agri-card p-6 sm:p-8">
        <div className="flex items-center gap-3"><div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center"><Database className="h-5 w-5" /></div><div><h2 className="text-lg font-black">How satellite features enter the project</h2><p className="text-xs text-slate-500">No raw imagery is directly fed to the model.</p></div></div>
        <div className="mt-7 grid gap-3 md:grid-cols-4">
          <Step n="01" title="Subset" text="7 Vidarbha districts are extracted through AppEEARS." />
          <Step n="02" title="Quality check" text="Coverage, missingness and layer values are validated." />
          <Step n="03" title="Aggregate" text="Pixel/time-series data become compact district-year features." />
          <Step n="04" title="Hindcast" text="Only forecast-origin-safe features are tested before integration." />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 text-xs leading-5 text-slate-600"><b className="text-slate-900">Review note:</b> “Complete” means the AppEEARS extraction is available; it does not mean the dataset has already improved the yield model. Every new feature family must pass the project's strict hindcast evaluation before production use.</section>
    </div>
  );
}

function DatasetCard({ name, period, features, status, icon: Icon, color }) { const complete = status === 'Complete'; const bg = complete ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'; return <div className="agri-card agri-card-hover p-5"><div className="flex items-start justify-between"><div className={`h-10 w-10 rounded-xl flex items-center justify-center ${bg}`}><Icon className="h-5 w-5" /></div><span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-extrabold ${complete ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>{complete ? <CheckCircle2 className="h-3 w-3" /> : <Clock3 className="h-3 w-3" />}{status}</span></div><h3 className="mt-5 text-base font-black">{name}</h3><p className="mt-1 text-xs text-slate-500">{period}</p><div className="mt-4 rounded-xl bg-slate-50 px-3 py-2 text-xs font-bold text-slate-700">{features}</div></div>; }
function Step({ n, title, text }) { return <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4"><div className="font-mono text-[10px] font-bold text-emerald-600">{n}</div><h3 className="mt-3 text-sm font-black">{title}</h3><p className="mt-1 text-xs leading-5 text-slate-500">{text}</p></div>; }
