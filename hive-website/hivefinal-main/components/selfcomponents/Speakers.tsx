"use client";

import Image from "next/image";
import React from "react";
import { CardBody, CardContainer, CardItem } from "@/components/ui/3d-card";
import Link from "next/link";
import { FaLinkedinIn } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";
import { HyperText } from "@/components/ui/hyper-text";
import { ShinyButton } from "@/components/ui/shiny-button";

const cardData = [
  {
    name: "Siv Ram Shastri",
    role: "Co-founder",
    company: "HYD DAO",
    image: "/images/speakers/Siv_Ram.png",
    linkedin: "https://www.linkedin.com/in/sivramshastri/",
    twitter: "https://x.com/sivramshastri",
  },
  {
    name: "Ruchi Bhatia",
    role: "Manager",
    company: "Hewlett-Packard",
    image: "/images/speakers/Ruchi Bhatia.jpg",
    linkedin: "https://www.linkedin.com/in/ruchi798/",
    twitter: "https://x.com/ruchi798",
  },
  {
    name: "Praveen Kumar Purushothaman",
    role: "UI Architecture",
    company: "Fitch Group",
    image: "/images/speakers/Praveen_kumar.jpg",
    linkedin: "https://www.linkedin.com/in/praveentech/",
    twitter: "https://x.com/praveenscience",
  },
  {
    name: "Madhu Vadlamani",
    role: "Influencer",
    company: "Miracle Software Systems",
    image: "/images/speakers/Madhu_vadlamani.jpg",
    linkedin: "https://www.linkedin.com/in/madhuvad/",
    twitter: "https://x.com/Madhu_Vad",
  },
  {
    name: "Varun Satyam",
    role: "Co-Founder and CEO",
    company: "Davos Protocol",
    image: "/images/speakers/Varun_satyam.png",
    linkedin: "https://www.linkedin.com/in/exportpng/",
    twitter: "https://x.com/exportpng",
  },
  {
    name: "Srishti Sharma",
    role: "Chief Executive Officer",
    company: "Automaxis",
    image: "/images/speakers/sristi_sharma.png",
    linkedin: "https://www.linkedin.com/in/srishti-sharma-9aa40651/",
    twitter: "https://x.com/SrishtiSharma_",
  },
  {
    name: "Puspanjali Sarma",
    role: "Senior Manager",
    company: "ServiceNow",
    image: "/images/speakers/pushpanjali.jpg",
    linkedin: "https://www.linkedin.com/in/puspanjalisarma/",
    twitter: "https://x.com/",
  },
  {
    name: "Rohan Kokkula",
    role: "Developer Relations Specialist",
    company: "Contentstack",
    image: "/images/speakers/rohan_kokkula.png",
    linkedin: "https://www.linkedin.com/in/rohankokkula/",
    twitter: "https://x.com/soberohan",
  },
  {
    name: "Sruthi Manthena",
    role: "Client Support Specialist",
    company: "Immunefi",
    image: "/images/speakers/sruthi_manthena.png",
    linkedin: "https://www.linkedin.com/in/sruthi-manthena-5b1a8b215/",
    twitter: "https://x.com/sruthi_2408",
  },
  {
    name: "Pranali Bose",
    role: "Machine Learning Engineer",
    company: "DBS Bank",
    image: "/images/speakers/pranali_bose.png",
    linkedin: "https://www.linkedin.com/in/pranalibose/",
    twitter: "https://x.com/pranalibose",
  },
];

export default function Speakers() {
  return (
    <>
      <div id="about" className="py-24 pb-5 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
            <HyperText>Speakers</HyperText>
          </h2>
        </div>
      </div>

      {/* Cards Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6 max-w-7xl mx-auto mb-5">
        {cardData.map( (person, index) => (
          <CardContainer key={index} className="inter-var">
            <CardBody className="relative group/card dark:hover:shadow-2xl dark:hover:shadow-emerald-500/[0.1] bg-black border-white/[0.2] w-[260px] h-[400px] rounded-xl p-6 border transition-all duration-300">
              
              {/* Speaker Image */}
              <CardItem translateZ="50" className="w-full flex justify-center">
                <div className="relative w-40 h-40">
                  <Image
                    src={person.image}
                    layout="fill"
                    className="object-cover border border-gray-300 rounded-xl"
                    alt={person.name}
                  />
                </div>
              </CardItem>

              {/* Speaker Name */}
              <CardItem translateZ="50" className="text-lg font-semibold text-white text-left mt-4">
                {person.name}
              </CardItem>

              {/* Speaker Role & Company */}
              <CardItem as="p" translateZ="60" className="text-sm text-left text-neutral-300">
                {person.role} at {person.company}
              </CardItem>

              {/* Social Media Links */}
              <div className="flex justify-center gap-4 mt-6">
                {person.linkedin && (
                  <a
                    href={person.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-200 transition"
                  >
                    <FaLinkedinIn className="h-5 w-5 text-black" />
                  </a>
                )}

                {person.twitter && (
                  <a
                    href={person.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-200 transition"
                  >
                    <FaXTwitter className="h-5 w-5 text-black" />
                  </a>
                )}
              </div>
            </CardBody>
          </CardContainer>
        ))}
      </div>

      {/* Join Us Button */}
      <div className="flex justify-center mt-6 mb-32">
        <Link
          href="https://docs.google.com/forms/d/e/1FAIpQLSegJyyWTRC3WxZfnvwMAe7g6akTSPPnfIdpZRft9pXGsf4xdQ/viewform?usp=header"
          target="_blank"
        >
          <ShinyButton>Join us</ShinyButton>
        </Link>
      </div>
    </>
  );
}
