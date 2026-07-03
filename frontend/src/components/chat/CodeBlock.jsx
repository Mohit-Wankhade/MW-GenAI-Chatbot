import { Copy, Check } from "lucide-react";
import { useState } from "react";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function CodeBlock({
    language,
    value
}) {

    const [copied, setCopied] = useState(false);

    function copyCode() {

        navigator.clipboard.writeText(value);

        setCopied(true);

        setTimeout(() => {

            setCopied(false);

        }, 2000);

    }

    return (

        <div className="relative my-5 rounded-xl overflow-hidden">

            <button

                onClick={copyCode}

                className="absolute right-3 top-3 bg-[#2c2f38] hover:bg-[#4b4d52] p-2 rounded-lg z-10"

            >

                {

                    copied

                        ? <Check size={16} />

                        : <Copy size={16} />

                }

            </button>

            <SyntaxHighlighter

                language={language}

                style={oneDark}

                customStyle={{

                    margin: 0,

                    borderRadius: "12px",

                    fontSize: "15px"

                }}

            >

                {value}

            </SyntaxHighlighter>

        </div>

    );

}