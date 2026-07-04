export default function ThinkingIndicator({ label = "Thinking", compact = false }) {
  return (
    <div className={`flex items-center gap-2 ${compact ? "px-0 py-0" : "px-2 py-1"}`}>
      <div className="flex items-center gap-1">
        <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
        <span
          className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
          style={{ animationDelay: "0.15s" }}
        />
        <span
          className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
          style={{ animationDelay: "0.3s" }}
        />
      </div>

      {label && (
        <span className="text-sm text-gray-300">
          {label}
        </span>
      )}
    </div>
  );
}