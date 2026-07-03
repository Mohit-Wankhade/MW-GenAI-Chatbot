export default function ThinkingIndicator() {

    return (

        <div className="flex gap-1 items-center px-2 py-1">

            <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></span>

            <span
                className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                style={{ animationDelay: "0.15s" }}
            ></span>

            <span
                className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                style={{ animationDelay: "0.3s" }}
            ></span>

        </div>

    );

}