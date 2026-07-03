export default function SuccessCard({

    title,

    items,

    footer,

    onContinue

}) {

    return (

        <div className="mt-6 rounded-2xl bg-[#242321] border border-[#3E3A34] p-6 text-left shadow-lg">

            <h3 className="text-[#C6A969] font-semibold text-xl">

                {title}

            </h3>

            <div className="mt-5 space-y-3">

                {items.map((item) => (

                    <div

                        key={item.label}

                        className="
                            flex
                            items-center
                            justify-between
                            rounded-xl
                            bg-[#1D1D1B]
                            border
                            border-[#34322F]
                            px-4
                            py-3
                        "

                    >

                        <span className="text-[#B9AE9F] flex items-center gap-2">

                            <span className="text-lg">

                                {item.icon}

                            </span>

                            {item.label}

                        </span>

                        <span className="font-semibold text-[#F4E7D3]">

                            {item.value}

                        </span>

                    </div>

                ))}

            </div>

            <p className="mt-5 text-sm text-[#CBB58A]">

                {footer}

            </p>

            <button

                onClick={onContinue}

                className="
                    mt-6
                    w-full
                    rounded-xl
                    bg-[#C6A969]
                    hover:bg-[#D4B67A]
                    text-[#1D1D1B]
                    font-semibold
                    py-3
                    transition-all
                    duration-200
                    shadow-md
                    hover:shadow-lg
                "

            >

                Continue →

            </button>

        </div>

    );

}