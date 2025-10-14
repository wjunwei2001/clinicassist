import { PatientState } from "@/types/api";

interface SidebarProps {
  state: PatientState;
  phase: string;
  isComplete: boolean;
}

function Badge({ children, tone = "info" }: { children: React.ReactNode; tone?: "info" | "success" | "warning" | "danger" }) {
  const toneClasses = {
    info: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300 dark:border-emerald-800",
    warning: "bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-900/20 dark:text-amber-200 dark:border-amber-800",
    danger: "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800",
  } as const;
  return <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${toneClasses[tone]}`}>{children}</span>;
}

function SectionCard({ title, icon, children }: { title: string; icon?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-900/40 rounded-t-xl">
        <h3 className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider flex items-center gap-2">
          {icon && <span className="text-base leading-none">{icon}</span>}
          {title}
        </h3>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

function KeyValue({ label, value }: { label: string; value?: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 items-baseline text-sm">
      <div className="text-slate-500 dark:text-slate-400 font-medium">{label}:</div>
      <div className="text-slate-900 dark:text-slate-100 font-semibold">{value ?? "—"}</div>
    </div>
  );
}

export default function Sidebar({ state, phase, isComplete }: SidebarProps) {
  const hasPatientInfo = Boolean(state.patient_name || state.patient_age || state.patient_sex);
  const hasSymptoms = Boolean(state.main_symptoms && state.main_symptoms.length > 0);
  const hasMedHistory = Boolean(state.medical_history && state.medical_history.length > 0);
  const hasSummary = Boolean(state.generated_summary);

  return (
    <div className="w-96 bg-gray-50 dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-gray-50/90 dark:bg-gray-900/90 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 px-5 py-4">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 tracking-tight">Patient Summary</h2>
      </div>

      <div className="p-4 space-y-4">
        {/* Demographics */}
        <SectionCard title="Demographics" icon="👤">
          {hasPatientInfo ? (
            <div className="space-y-2">
              <KeyValue label="Name" value={state.patient_name} />
              <KeyValue label="Age" value={state.patient_age ? `${state.patient_age} years` : undefined} />
              <KeyValue label="Sex" value={state.patient_sex === "M" ? "Male" : state.patient_sex === "F" ? "Female" : undefined} />
            </div>
          ) : (
            <div className="text-sm text-slate-400 dark:text-slate-500 italic">Awaiting patient information...</div>
          )}
        </SectionCard>

        {/* Chief Complaint */}
        <SectionCard title="Chief Complaint" icon="🩺">
          {hasSymptoms ? (
            <div className="space-y-4">
              {state.main_symptoms && state.main_symptoms.length > 0 && (
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 font-semibold mb-1">Presenting symptoms</div>
                  <ul className="list-disc list-inside space-y-1 text-sm text-slate-900 dark:text-slate-100">
                    {state.main_symptoms.map((symptom, idx) => (
                      <li key={idx} className="leading-snug">{symptom}</li>
                    ))}
                  </ul>
                </div>
              )}

              {state.symptom_onset && (
                <div className="pt-3 border-t border-slate-200 dark:border-gray-700">
                  <div className="text-xs text-slate-500 dark:text-slate-400 font-semibold mb-1">Onset</div>
                  <ul className="list-disc list-inside space-y-1 text-sm text-slate-900 dark:text-slate-100">
                    <li className="leading-snug">{state.symptom_onset}</li>
                  </ul>
                </div>
              )}

              {state.associated_symptoms && state.associated_symptoms.length > 0 && (
                <div className="pt-3 border-t border-slate-200 dark:border-gray-700">
                  <div className="text-xs text-slate-500 dark:text-slate-400 font-semibold mb-1">Associated symptoms</div>
                  <ul className="list-disc list-inside space-y-1 text-sm text-slate-900 dark:text-slate-100">
                    {state.associated_symptoms.map((symptom, idx) => (
                      <li key={idx} className="leading-snug">{symptom}</li>
                    ))}
                  </ul>
                </div>
              )}

              {state.additional_symptom_info && state.additional_symptom_info.length > 0 && (
                <div className="pt-3 border-t border-slate-200 dark:border-gray-700">
                  <div className="text-xs text-slate-500 dark:text-slate-400 font-semibold mb-1">Clinical notes</div>
                  <ul className="list-disc list-inside space-y-1 text-sm text-slate-700 dark:text-slate-300">
                    {state.additional_symptom_info.map((info, idx) => (
                      <li key={idx} className="leading-relaxed">{info}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-sm text-slate-400 dark:text-slate-500 italic">Awaiting symptom details...</div>
          )}
        </SectionCard>

        {/* Medical History */}
        <SectionCard title="Medical History" icon="📋">
          {hasMedHistory ? (
            <div className="space-y-2.5">
              {state.medical_history!.map((fact, idx) => (
                <div key={idx} className="p-3 rounded-lg border border-slate-200 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="text-[10px] font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                      {fact.category.replace("_", " ")}
                    </div>
                  </div>
                  <div className="text-xs font-semibold mb-1 leading-tight text-slate-900 dark:text-slate-100">
                    {fact.question}
                  </div>
                  <div className="text-sm font-medium leading-snug text-slate-800 dark:text-slate-200">
                    {fact.answer}
                  </div>
                  {fact.additional_details && (
                    <div className="text-xs mt-1.5 opacity-80 leading-relaxed text-slate-700 dark:text-slate-300">
                      {fact.additional_details}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-slate-400 dark:text-slate-500 italic">Awaiting medical history...</div>
          )}
        </SectionCard>

        {/* Clinical Assessment */}
        {hasSummary && (
          <SectionCard title="Clinical Assessment" icon="⚕️">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase">Urgency</div>
                <Badge
                  tone={
                    state.generated_summary!.urgency === "EMERGENCY"
                      ? "danger"
                      : state.generated_summary!.urgency === "URGENT"
                      ? "warning"
                      : state.generated_summary!.urgency === "SEMI-URGENT"
                      ? "warning"
                      : "success"
                  }
                >
                  {state.generated_summary!.urgency}
                </Badge>
              </div>

              <div className="rounded-lg border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-900/40 p-3">
                <div className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase mb-1.5">Clinical rationale</div>
                <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                  {state.generated_summary!.reason_for_urgency}
                </div>
              </div>

              <div>
                <div className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase mb-2">Working diagnosis</div>
                <div className="text-base font-bold text-slate-900 dark:text-slate-100 mb-2 leading-tight">
                  {state.generated_summary!.probable_diagnosis}
                </div>
                <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-3">
                  <div className="text-xs text-blue-900 dark:text-blue-200 leading-relaxed">
                    {state.generated_summary!.reason_for_diagnosis}
                  </div>
                </div>
              </div>
            </div>
          </SectionCard>
        )}
      </div>
    </div>
  );
}

