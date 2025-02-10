"use client"
import React from 'react';
import { HyperText } from "@/components/ui/hyper-text";
import { Plus, Minus } from 'lucide-react';

const FAQ = () => {
  const [openIndex, setOpenIndex] = React.useState<number | null>(null);

  const faqs = [
    {
      question: "What is Hack to the Hive?",
      answer: "Hack to the Hive is a 3-day hackathon focused on Web3 and blockchain technology innovation. It brings together developers, designers, and entrepreneurs to build cutting-edge solutions."
    },
    {
      question: "Who can participate?",
      answer: "Anyone with a passion for blockchain and Web3 technology can participate. Whether you're a student, professional, or enthusiast, you're welcome to join!"
    },
    {
      question: "Do I need a team?",
      answer: "While you can work solo, we encourage team participation. Don't worry if you don't have a team - we'll have team formation activities at the start of the event."
    },
    {
      question: "What should I bring?",
      answer: "Bring your laptop, charger, and any other devices you'll need for development. We'll provide food, drinks, and a comfortable hacking space."
    },
    {
      question: "Is there a participation fee?",
      answer: "No, participation is completely free! We believe in making innovation accessible to everyone."
    }
  ];

  return (
    <section id="faq" className="relative py-24 bg-black overflow-hidden">
      <div className="stars-1"></div>
      <div className="stars-2"></div>
      <div className="stars-3"></div>
      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="font-poppins text-4xl font-extrabold text-white sm:text-5xl">
            <HyperText>FAQ's</HyperText>
          </h2>
        </div>
        <div className="space-y-4 mt-6">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white/10 border border-white/20 backdrop-blur-lg shadow-lg rounded-2xl overflow-hidden"
            >
              <button
                className="w-full px-6 py-4 flex items-center justify-between text-left"
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
              >
                <span className="text-lg font-poppins text-white">{faq.question}</span>
                {openIndex === index ? (
                  <Minus className="w-5 h-5 text-white/80" />
                ) : (
                  <Plus className="w-5 h-5 text-white/80" />
                )}
              </button>
              {openIndex === index && (
                <div className="px-6 pb-4">
                  <p className="text-white/80 font-sans">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FAQ;
