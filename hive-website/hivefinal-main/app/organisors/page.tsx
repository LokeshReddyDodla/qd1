"use client";
import React from "react";
import { HyperText } from "@/components/ui/hyper-text";
import Image from "next/image";

const committees = [
  {
    name: "Operations & Logistics Committee",
    members: [
      { role: "Head", name: "Chandrabose Pachetti", size: "L", image: "/images/organisers/bose.png" },
      { role: "Head", name: "Lokesh Jampana", size: "XXL", image: "/images/organisers/lokeshj.png" },
      { role: "Co-Head", name: "Sai Puneeth Reddypally", size: "M", image: "/images/organisers/puneeth.png" },
    ],
  },
  {
    name: "Finance Committee",
    members: [
      { role: "Head", name: "Sai Santhosh Dasu", size: "L", image: "/images/organisers/santosh.png" },
    ],
  },
  
  {
    name: "Discipline & Security Committee",
    members: [
      { role: "Head", name: "Lokesh Kasala", size: "M", image: "/images/organisers/lokeshk.png" },
    ],
  },
  {
    name: "Hospitality & Logistics Committee",
    members: [
      { role: "Head", name: "Manosree Kallepalli", size: "", image: "/images/organisers/manosree.png" },
      { role: "Head", name: "Lokesh Reddy Dodla", size: "M", image: "/images/organisers/Lokeshreddy.png" },
      { role: "Head", name: "D N Nithin", size: "XXL", image: "/images/organisers/nithin.png" },
      { role: "Co-Head", name: "K Avinash", size: "L", image: "/images/organisers/avinash.png" },
      { role: "Co-Head", name: "Sanjay Nangunuru", size: "L", image: "/images/organisers/sanjay.png" },
      
    ],
  },
  {
    name: "Marketing & Promotions Committee",
    members: [
      { role: "Head", name: "Manaswi Amberi", size: "XL", image: "/images/organisers/manashwi.png" },
    ],
  },
  {
    name: "Community Engagement & Sponsorship Committee",
    members: [
      { role: "Head", name: "Pranakya Puligila", size: "XS/S", image: "/images/organisers/pranakya.png" },
      { role: "Co-Head", name: "Thirumalesh Pininnti", size: "M", image: "/images/organisers/tirmalesh.png" },
      
      
    ],
  },
  {
    name: "Media & Photography Committee",
    members: [
      { role: "Head", name: "Bharath Kummari", size: "XL", image: "/images/organisers/Bharath.png" },
    ],
  },
  
  {
    name: "Help Desk & Support Committee",
    members: [
      { role: "Head", name: "Laalithya Prakki", size: "M", image: "/images/organisers/laalitya.png" },
    ],
  },
  {
    name: "Public Outreach Committee",
    members: [
      { role: "Head", name: "Ashwan Uyyala", size: "M", image: "/images/organisers/ashwan.png" },
    ],
  },
  {
    name: "Event Coordination Committee",
    members: [
      { role: "Head", name: "Geetanjali Siddabathini", size: "S", image: "/images/organisers/geetanjali.png" },
    ],
  },
  {
    name: "Design Committee",
    members: [
      { role: "Head", name: "Kiran Kummari", size: "M", image: "/images/organisers/kiran.png" },
    ],
  },
];

export default function Organisers() {
  return (
    <div id="organisers" className="py-24 bg-black flex justify-center items-center flex-col">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="font-mono text-9xl font-extrabold text-white mb-8">
          <HyperText>Organisers</HyperText>
        </h1>
        
        {committees.map((committee, index) => (
          <div key={index} className="mb-16">
            <h2 className="font-anton text-5xl font-bold text-white mb-8">
              {committee.name}
            </h2>
            <div className="flex flex-wrap justify-center gap-8">
              {committee.members.map((member, mIndex) => (
                <div
                  key={mIndex}
                  className="bg-white/10 backdrop-blur-lg border border-white/20 p-6 rounded-lg text-center flex flex-col items-center w-64 h-65"
                >
                  <Image
                    src={member.image}
                    alt={member.name}
                    className="w-40 h-40 rounded-lg mb-4 object-cover"
                    style={{ aspectRatio: "1 / 1" }}
                    width="2000" height="2000"
                  />
                  <p className="text-lg font-semibold text-white">{member.name} </p>
                  <p className="text-sm text-gray-300 mb-4">{member.role}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}