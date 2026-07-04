export default function AuthLayout({ children }) {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#171717] px-4 py-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(200,169,126,0.18),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(255,255,255,0.08),transparent_30%)]" />

      <div className="relative w-full max-w-md rounded-3xl border border-white/10 bg-[#2f2f2f]/95 p-8 shadow-2xl backdrop-blur">
        {children}
      </div>
    </main>
  );
}