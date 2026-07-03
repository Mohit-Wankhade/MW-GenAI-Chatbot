import { useState, useEffect } from "react";
import { FaGithub } from "react-icons/fa";
import { Loader2 } from "lucide-react";
import SuccessCard from "../common/SuccessCard";
import { indexGithub } from "../../services/githubService";

export default function GithubForm({ onSuccess }) {

    const [url, setUrl] = useState("");

    const [loading, setLoading] = useState(false);

    const [seconds, setSeconds] = useState(0);

    const [result, setResult] = useState(null);

    useEffect(() => {

        if (!loading) {

            setSeconds(0);

            return;

        }

        const interval = setInterval(() => {

            setSeconds(prev => prev + 1);

        }, 1000);

        return () => clearInterval(interval);

    }, [loading]);

    async function handleSubmit(e) {

        e.preventDefault();

        if (!url.trim()) return;

        try {

            setLoading(true);

            setResult(null);

            const data = await indexGithub(url);

            setResult(data);

        }

        catch (err) {

            console.error(err);

            setResult({

                error: true,

                message: "Failed to index repository."

            });

        }

        finally {

            setLoading(false);

        }

    }

    return (

        <form onSubmit={handleSubmit} className="space-y-6">

            <div>

                <label className="block text-sm text-[#CBB58A] mb-2">

                    GitHub Repository URL

                </label>

                <input

                    value={url}

                    onChange={(e) => setUrl(e.target.value)}

                    placeholder="https://github.com/user/repository"

                    className="
                        w-full
                        rounded-xl
                        bg-[#242321]
                        border
                        border-[#3E3A34]
                        px-4
                        py-3
                        outline-none
                        text-[#F4E7D3]
                        placeholder:text-[#7B746B]
                        focus:border-[#C6A969]
                        transition
                    "

                />

            </div>

            <button

                disabled={loading}

                className="
                    w-full
                    rounded-xl
                    py-3
                    flex
                    items-center
                    justify-center
                    gap-2
                    bg-[#C6A969]
                    hover:bg-[#D4B67A]
                    text-[#1D1D1B]
                    font-semibold
                    transition-all
                    duration-200
                    disabled:opacity-70
                "

            >

                {loading ? (

                    <>

                        <Loader2
                            className="animate-spin"
                            size={18}
                        />

                        Indexing... ({seconds}s)

                    </>

                ) : (

                    <>

                        <FaGithub size={18} />

                        Index Repository

                    </>

                )}

            </button>

            {loading && (

                <div className="rounded-xl bg-[#242321] border border-[#3E3A34] p-4">

                    <div className="w-full h-2 bg-[#34322F] rounded-full overflow-hidden">

                        <div

                            className="h-full bg-[#C6A969] animate-pulse"

                            style={{

                                width: "100%"

                            }}

                        />

                    </div>

                    <p className="text-sm text-[#B9AE9F] text-center mt-3">

                        Cloning repository → Reading files →
                        Creating embeddings → Building index...

                    </p>

                </div>

            )}

            {result && (

                result.error ? (

                    <div className="mt-4 rounded-xl bg-red-900/20 border border-red-800 p-4 text-red-300">

                        ❌ {result.message}

                    </div>

                ) : (

                    <SuccessCard

                        title="Repository Indexed Successfully"

                        items={[

                            {

                                icon: "💻",

                                label: "Repository",

                                value: result.repo

                            },

                            {

                                icon: "📄",

                                label: "Files Indexed",

                                value: result.files

                            },

                            {

                                icon: "🧩",

                                label: "Chunks",

                                value: result.chunks

                            }

                        ]}

                        footer="Repository is ready for AI-powered code questions."

                        onContinue={onSuccess}

                    />

                )

            )}

        </form>

    );

}