import { cn } from "@/lib/utils";
import React from "react";
import { BentoGrid, BentoGridItem } from "@/components/ui/bento-grid";
import { HyperText } from "@/components/ui/hyper-text";
import {
  IconArrowWaveRightUp,
  IconBoxAlignRightFilled,
  IconBoxAlignTopLeft,
  IconClipboardCopy,
  IconFileBroken,
  IconSignature,
  IconTableColumn,
} from "@tabler/icons-react";

export function PastEvents() {
  return (
    <>
      <div id="about" className="py-24 bg-black">
        {/* Full width container with padding to leave some space on the sides */}
        <div className="w-full px-4">
          <div className="text-center">
            <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
              <HyperText>PAST EVENTS</HyperText>
            </h2>
            <p className="mt-4 text-xl text-white/80 font-sans">
              Join us in pushing the boundaries of blockchain technology and Web3 innovation
            </p>
          </div>
        </div>
      </div>
      {/* BentoGrid container with responsive padding */}
      <BentoGrid className="w-full px-4">
        {items.map((item, i) => (
          <BentoGridItem
            key={i}
            title={item.title}
            description={item.description}
            header={item.header}
            icon={item.icon}
            className={cn(
              // For larger screens, some items span two columns
              i === 3 || i === 6 ? "md:col-span-2" : "",
              // Responsive min-height: 12rem on mobile, 16rem on medium and up
              "min-h-[12rem] md:min-h-[16rem]"
            )}
          />
        ))}
      </BentoGrid>
    </>
  );
}

const Skeleton = ({ imageUrl }: { imageUrl: string }) => (
  <div className="flex flex-1 w-full h-full min-h-[12rem] md:min-h-[8rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800">
    <img src={imageUrl} alt="" className="w-full h-full object-cover rounded-xl" />
  </div>
);

const items = [
  {
    title: "The Dawn of Innovation",
    description: "Explore the birth of groundbreaking ideas and inventions.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconClipboardCopy className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "The Digital Revolution",
    description: "Dive into the transformative power of technology.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconFileBroken className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "The Art of Design",
    description: "Discover the beauty of thoughtful and functional design.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconSignature className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "The Power of Communication",
    description: "Understand the impact of effective communication in our lives.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconTableColumn className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "The Pursuit of Knowledge",
    description: "Join the quest for understanding and enlightenment.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconArrowWaveRightUp className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "The Joy of Creation",
    description: "Experience the thrill of bringing ideas to life.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconBoxAlignTopLeft className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "The Spirit of Adventure",
    description: "Embark on exciting journeys and thrilling discoveries.",
    header: <Skeleton imageUrl="/hero.jpg" />,
    icon: <IconBoxAlignRightFilled className="h-4 w-4 text-neutral-500" />,
  },
];
