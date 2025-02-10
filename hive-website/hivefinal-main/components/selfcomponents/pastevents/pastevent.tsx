import { cn } from "@/lib/utils";
import React from "react";
import { BentoGrid, BentoGridItem } from "@/components/ui/bento-grid";
import { HyperText } from "@/components/ui/hyper-text";

export function PastEvents() {
  return (
    <section className="bg-[url('/hero2.jpg')] bg-cover bg-center overflow-hidden">
      <div id="about" className="py-24 pb-5 bg-black bg-opacity-60">
        {/* Full width container with padding to leave some space on the sides */}
        <div className="w-full px-4">
          <div className="text-center">
            <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
              <HyperText>PAST EVENTS</HyperText>
            </h2>
          </div>
        </div>
      </div>
      {/* BentoGrid container with responsive padding */}
      <BentoGrid className="w-full sm:w-3/4 md:w-4/5 lg:w-3/4 px-4 mx-auto">
        {items.map((item, i) => (
          <BentoGridItem
            key={i}
            title={item.title}
            description={item.description}
            header={item.header}
            className={cn(
              // For larger screens, some items span two columns
              i === 3 || i === 6 ? "md:col-span-2" : "",
              // Responsive min-height: 12rem on mobile, 16rem on medium and up
              "min-h-[12rem] md:min-h-[16rem] rounded-xl overflow-hidden"
            )}
          />
        ))}
      </BentoGrid>
    </section>
  );
}

const Skeleton = ({ imageUrl }: { imageUrl: string }) => (
  <div className="flex flex-1 w-full h-full min-h-[12rem] md:min-h-[8rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800">
    <img src={imageUrl} alt="" className="w-full h-full object-cover rounded-xl" />
  </div>
);

const items = [
  {
    title: "Hackthons",
    description: `Dynamic coding challenges where participants collaborated to develop innovative solutions under time constraints.`,
    header: <Skeleton imageUrl="/images/WhatsApp Image 2025-02-06 at 08.19.58_7977c19e.jpg" />,
  },
  {
    title: "Bootcamps",
    description: "Comprehensive, hands-on training programs that equipped participants with advanced technical skills and practical knowledge.",
    header: <Skeleton imageUrl="/images/WhatsApp Image 2025-02-06 at 06.38.52_50385ab1.jpg" />,
  },
  {
    title: "Workshops",
    description: "Focused, interactive sessions that provided in-depth learning experiences in emerging technologies.",
    header: <Skeleton imageUrl="/images/3.jpg" />,
  },
  {
    title: "Tech Talks",
    description: "Focused, interactive sessions that provided in-depth learning experiences in emerging technologies.",
    header: <Skeleton imageUrl="/images/4.jpg" />,
  },
  {
    title: "Coding Camps",
    description: "Immersive learning experiences designed to enhance programming skills through real-world projects and expert mentorship.",
    header: <Skeleton imageUrl="/images/5.jpg" />,
  },
];