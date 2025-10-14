interface ProgressBarProps {
  phase: string;
  isComplete: boolean;
}

export default function ProgressBar({ phase, isComplete }: ProgressBarProps) {
  const stages = [
    { id: 1, name: "Patient Info", phase: "Gathering patient demographic details" },
    { id: 2, name: "Symptoms", phase: "Symptoms collection" },
    { id: 3, name: "Medical History", phase: "Medical/health history" },
    { id: 4, name: "Triage", phase: "Triage & summary" },
  ];

  // Map phase string to current stage based on exact backend phase strings
  const getCurrentStage = () => {
    if (isComplete || phase === "Complete") return 5; // All stages complete
    
    const stageIndex = stages.findIndex(stage => stage.phase === phase);
    if (stageIndex !== -1) {
      return stages[stageIndex].id;
    }
    
    return 0; // Not started
  };

  const currentStage = getCurrentStage();

  return (
    <div className="w-full flex justify-center">
      <div className="flex items-center max-w-2xl">
        {stages.map((stage, index) => (
          <div key={stage.id} className="flex items-center">
            {/* Stage Circle */}
            <div className="flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  stage.id < currentStage
                    ? "bg-emerald-500 text-white"
                    : stage.id === currentStage
                    ? "bg-blue-600 text-white ring-4 ring-blue-200 dark:ring-blue-900"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                }`}
              >
                {stage.id < currentStage ? "✓" : stage.id}
              </div>
              <div
                className={`mt-1.5 text-xs font-medium whitespace-nowrap ${
                  stage.id <= currentStage
                    ? "text-slate-900 dark:text-slate-100"
                    : "text-gray-400 dark:text-gray-500"
                }`}
              >
                {stage.name}
              </div>
            </div>

            {/* Connector Line */}
            {index < stages.length - 1 && (
              <div className="w-24 h-1 mx-3 relative top-[-10px]">
                <div
                  className={`h-full rounded transition-all ${
                    stage.id < currentStage
                      ? "bg-emerald-500"
                      : "bg-gray-200 dark:bg-gray-700"
                  }`}
                ></div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

