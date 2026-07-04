export default function SuccessCard({
  title = "Success",
  items = [],
  footer = "",
  onContinue,
  continueLabel = "Continue",
}) {
  return (
    <div className="mt-6 rounded-2xl border border-[#3E3A34] bg-[#242321] p-6 text-left shadow-lg">
      <h3 className="text-xl font-semibold text-[#C6A969]">
        {title}
      </h3>

      {items.length > 0 && (
        <div className="mt-5 space-y-3">
          {items.map((item, index) => (
            <div
              key={`${item.label}-${index}`}
              className="flex items-center justify-between gap-4 rounded-xl border border-[#34322F] bg-[#1D1D1B] px-4 py-3"
            >
              <span className="flex min-w-0 items-center gap-2 text-[#B9AE9F]">
                {item.icon && (
                  <span className="text-lg">
                    {item.icon}
                  </span>
                )}

                <span className="truncate">
                  {item.label}
                </span>
              </span>

              <span
                className="max-w-[55%] truncate text-right font-semibold text-[#F4E7D3]"
                title={String(item.value ?? "")}
              >
                {item.value ?? "-"}
              </span>
            </div>
          ))}
        </div>
      )}

      {footer && (
        <p className="mt-5 text-sm leading-6 text-[#CBB58A]">
          {footer}
        </p>
      )}

      {onContinue && (
        <button
          type="button"
          onClick={onContinue}
          className="mt-6 w-full rounded-xl bg-[#C6A969] py-3 font-semibold text-[#1D1D1B] shadow-md transition-all duration-200 hover:bg-[#D4B67A] hover:shadow-lg"
        >
          {continueLabel} →
        </button>
      )}
    </div>
  );
}