import React from "react";
import { HyperText } from "@/components/ui/hyper-text";


const committees = [
  {
    name: "Operations & Logistics Committee",
    members: [
      { role: "Head", name: "Chandrabose Pachetti", size: "L", image: "https://via.placeholder.com/100" },
      { role: "Head", name: "Lokesh Jampana", size: "XXL", image: "https://via.placeholder.com/100" },
      { role: "Co-Head", name: "Sai Puneeth Reddypally", size: "M", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Finance Committee",
    members: [
      { role: "Head", name: "Sai Santhosh Dasu", size: "L", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Food Committee",
    members: [
      { role: "Head", name: "Lokesh Reddy Dodla", size: "M", image: "https://via.placeholder.com/100" },
      { role: "Co-Head", name: "K Avinash", size: "L", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Discipline & Security Committee",
    members: [
      { role: "Head", name: "Lokesh Kasala", size: "M", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Hospitality Committee",
    members: [
      { role: "Head", name: "Manosree Kallepalli", size: "", image: "https://via.placeholder.com/100" },
      { role: "Co-Head", name: "Sanjay Nangunuru", size: "L", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Marketing & Promotions Committee",
    members: [
      { role: "Head", name: "Manaswi Amberi", size: "XL", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Sponsorship Committee",
    members: [
      { role: "Head", name: "Pranakya Puligila", size: "XS/S", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Media & Photography Committee",
    members: [
      { role: "Head", name: "Bharath Kummari", size: "XL", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Community Partnerships Committee",
    members: [
      { role: "Head", name: "Thirumalesh Pininnti", size: "M", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Help Desk & Support Committee",
    members: [
      { role: "Head", name: "Laalithya Prakki", size: "M", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Accommodation & Transport Committee",
    members: [
      { role: "Head", name: "D N Nithin", size: "XXL", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Public Outreach Committee",
    members: [
      { role: "Head", name: "Ashwan Uyyala", size: "M", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Event Coordination Committee",
    members: [
      { role: "Head", name: "Geetanjali Siddabathini", size: "S", image: "https://via.placeholder.com/100" },
    ],
  },
  {
    name: "Design Committee",
    members: [
      { role: "Head", name: "Kiran Kummari", size: "M", image: "https://via.placeholder.com/100" },
    ],
  },
];

export default function Organisers() {
  return (
    <div id="organisers" className="py-24 bg-black flex justify-center items-center flex-col">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="font-mono text-5xl font-extrabold text-white mb-8">
          <HyperText>Organisers</HyperText>
        </h1>
        <p className="mt-4 text-xl text-white/80 mb-16">
          Join us in pushing the boundaries of blockchain technology and Web3 innovation.
        </p>
        
        {committees.map((committee, index) => (
          <div key={index} className="mb-16">
            <h2 className="font-anton text-5xl font-bold text-white mb-8">
              {committee.name}
            </h2>
            <div className="flex flex-wrap justify-center gap-8">
              {committee.members.map((member, mIndex) => (
                <div
                  key={mIndex}
                  className="bg-white/10 backdrop-blur-lg border border-white/20 p-6 rounded-lg text-center flex flex-col items-center w-64 h-80"
                >
                  <img
                    src={member.image}
                    alt={member.name}
                    className="w-24 h-24 rounded-full mb-4"
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