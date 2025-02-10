import { FocusCards } from "@/components/ui/focus-cards";
import { HyperText } from "@/components/ui/hyper-text";

export default function FocusCardsDemo() {
      const cards = [
      {
        title: "🏆 Grand Prize  $1000",
        description: "The Ultimate Champion Outthink, outcode, and outshine to claim the grand $1000 prize! Plus, score some exclusive swags!",
        image: "https://images.unsplash.com/photo-1518710843675-2540dd79065c?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      },
      {
        title: "🌐 Web3",
        description: ` "Revolutionize the decentralized world and win $100—along with epic swags!"`,
        image: "https://images.unsplash.com/photo-1600271772470-bd22a42787b3?q=80&w=3072&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      },
      {
        title: "🧠 Gen AI ",
        description:` "Push the limits of AI intelligence, grab $100, and flex your exclusive swags!"`,
        image: "https://images.unsplash.com/photo-1505142468610-359e7d316be0?q=80&w=3070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      },
      {
        title: " 💻 Web2",
        description: ` "Innovate the digital experience, pocket $100, and rock some awesome swags!"`,
        image: "https://images.unsplash.com/photo-1486915309851-b0cc1f8a0084?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      },
      {
        title: "🚀 Open Source ",
        description: ` "Empower the community with open innovation, win $100, and take home cool swags!"`,
        image: "https://images.unsplash.com/photo-1507041957456-9c397ce39c97?q=80&w=3456&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      },
    ];
  
    
  


 
    

  return (
    <section className="bg-[url('/hero2.jpg')] bg-contain overflow-hidden">
     <div id="about" className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-poppins text-4xl font-extrabold text-white sm:text-5xl">
           <HyperText > prize </HyperText>
          </h2>       
          </div>
        </div>

    <FocusCards cards={cards} />
  </section>   
  
);
}
