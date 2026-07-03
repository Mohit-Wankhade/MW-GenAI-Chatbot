export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-[#212121] flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-[#2f2f2f] rounded-2xl shadow-2xl p-8 border border-gray-700">

        {children}

      </div>

    </div>
  );
}