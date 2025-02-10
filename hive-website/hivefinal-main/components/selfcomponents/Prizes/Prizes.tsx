import { HyperText } from "@/components/ui/hyper-text";

export default function FocusCardsDemo() {
  const cards = [
    {
      title: "🏆 The Ultimate Champion - $1000 + Exclusive Perks & Swags!",
      description: "Outthink, outcode, and outshine to seize the grand prize and unlock additional rewards!",
      image: "/images/1738779891152-mainremovebgpreview.png",
    },
    {
      title: "🌐 Prize $100",
      description: "Exclusive Perks & Swags!",
      image: "/images/1738779722882-web3removebgpreview.png",
    },
    {
      title: "🧠 Prize $100",
      description: "Exclusive Perks & Swags!",
      image: "/images/1738779871376-genairemovebgpreview.png",
    },
    {
      title: "💻 Prize $100",
      description: "Exclusive Perks & Swags!",
      image: "/images/1738779765233-web2removebgpreview.png",
    },
    {
      title: "🚀 Prize $100",
      description: "Exclusive Perks & Swags!",
      image: "/images/1738779933917-opensourceremovebgpreview.png",
    },
  ];

  return (
    <section className="bg-[url('/hero2.jpg')] bg-contain overflow-hidden">
      <div id="about" className="py-12 pb-5 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-poppins text-4xl font-extrabold text-white sm:text-5xl">
            <HyperText>prizes</HyperText>
          </h2>
        </div>
      </div>

      <div className="space-y-6 p-4 sm:p-6">
        <div className="p-4 sm:p-8 flex flex-col items-center">
          <div className="relative w-64 h-64">
            <img
              src={cards[0].image}
              alt={cards[0].title}
              className="absolute inset-0 h-full w-full object-contain"
            />
            <div className="absolute inset-x-0 bottom-0 h-1/6 bg-gradient-to-t from-white opacity-30"></div>
          </div>
          <p className="text-base sm:text-xl mt-4 mb-1 text-neutral-200 font-poppins text-center">
            {cards[0].title}
          </p>
          <p className="text-sm text-neutral-400 font-poppins text-center">
            {cards[0].description}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {cards.slice(1).map((card, index) => (
            <div key={index} className="p-4 sm:p-8">
              <div className="relative w-full" style={{ paddingBottom: "100%" }}>
                <img
                  src={card.image}
                  alt={card.title}
                  className="absolute inset-0 h-full w-full object-contain"
                />
                <div className="absolute inset-x-0 bottom-0 h-1/6 bg-gradient-to-t from-white opacity-20"></div>
              </div>
              <p className="text-base sm:text-xl mt-4 mb-1 text-neutral-200 font-bold font-poppins text-center">
                {card.title}
              </p>
              <p className="text-sm text-neutral-400 font-poppins text-center">
                {card.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}