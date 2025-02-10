"use client";
import Image from "next/image";
import React, { useState } from "react";
import { cn } from "@/lib/utils";

type CardProps = {
  title: string;
  image: string;
  description: string;
};

export const Card = React.memo(
  ({
    card,
    index,
    hovered,
    setHovered,
    className
  }: {
    card: CardProps;
    index: number;
    hovered: number | null;
    setHovered: React.Dispatch<React.SetStateAction<number | null>>;
    className?:string
  }) => (
    <div
      onMouseEnter={() => setHovered(index)}
      onMouseLeave={() => setHovered(null)}
      className={cn(
        "rounded-lg relative bg-gray-100 dark:bg-neutral-900 overflow-hidden h-60 md:h-96 w-full transition-all duration-300 ease-out",
        hovered !== null && hovered !== index && "blur-sm scale-[0.98]",className
      )}
    >
      <Image
        src={card.image}
        alt={card.title}
        fill
        className="object-cover absolute inset-0"
      />
      <div className="absolute inset-0 flex items-center justify-center text-white text-2xl font-bold"> {/* Hero text overlay */}
        {card.title} {/* Displaying the title as hero text */}
      </div>
      <div
        className={cn(
          "absolute inset-0 bg-black/50 flex items-end py-8 px-4 transition-opacity duration-300",
          hovered === index ? "opacity-100" : "opacity-0"
        )}
      >
        <div className="text-sm text-white">{card.description}</div> {/* Added description */}
      </div>       
      </div>
  
  ));

Card.displayName = "Card";

type Card = {
  title: string;
  src: string;
};

export function FocusCards({ cards }: { cards: CardProps[] }) {
  const [hovered, setHovered] = useState<number | null>(null);

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-10 max-w-5xl mx-auto md:px-8 w-full">
      {cards.map((card, index) => (
        <Card
          key={card.title}
          card={card}
          index={index}
          hovered={hovered}
          setHovered={setHovered}
          className={cn(
            index === 0 && "md:col-span-4 font-poppins"
          )}
        />
      ))}
    </div>
  );
}
