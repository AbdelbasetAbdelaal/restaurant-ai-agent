export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] gap-3">
      <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-sm text-slate-500 font-medium">Checking system status...</p>
    </div>
  );
}
