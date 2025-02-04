import { FocusCards } from "@/components/ui/focus-cards";
import { HyperText } from "@/components/ui/hyper-text";

export default function FocusCardsDemo() {


  const cards = [
    {
      title: "Grand Prize - Reward of $1000+",
      src: "https://images.unsplash.com/photo-1518710843675-2540dd79065c?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      description:"Reward prize money  of over $1000+ ",
    },
    {
      title: "Gen-AI Track- Reward $100+",
      src: "https://images.unsplash.com/photo-1600271772470-bd22a42787b3?q=80&w=3072&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      description:"Reward over $100+",
    },
    {
      title: "Web3 Track- Reward $100+",
      src: "https://images.unsplash.com/photo-1505142468610-359e7d316be0?q=80&w=3070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      description:"Reward over $100+",
    },
    {
      title: "Web2 Track- Reward $100+",
      src: "https://images.unsplash.com/photo-1486915309851-b0cc1f8a0084?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      description:"Reward over $100+",
    },
    {
      title: "Opensource Track- Reward $100+",
      src: "https://images.unsplash.com/photo-1507041957456-9c397ce39c97?q=80&w=3456&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      description:"Reward over $100+",
    },
   
  ];

  return (
    <>
     <div id="about" className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
           <HyperText > prize </HyperText>
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-white/80 font-sans">
            Join us in pushing the boundaries of blockchain technology and Web3 innovation
          </p>
        </div>
        </div>
        </div>

    <FocusCards cards={cards} />
  </>   
  
);
}
