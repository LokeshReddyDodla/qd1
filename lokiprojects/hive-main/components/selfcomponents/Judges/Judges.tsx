import React from 'react';
import JudgeCard from './JudgeCard';

const Judges = () => {
  const judges = [
    {
      name: 'Elena Martinez',
      role: 'Lead Blockchain Architect',
      company: 'Ethereum Foundation',
      expertise: ['Smart Contracts', 'DeFi', 'Security'],
      image: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=400&fit=crop',
      linkedin: 'https://linkedin.com',
    },
    {
      name: 'David Kim',
      role: 'VP of Engineering',
      company: 'Web3 Ventures',
      expertise: ['Infrastructure', 'Scalability', 'Zero Knowledge'],
      image: 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop',
      linkedin: 'https://linkedin.com',
    },
  ];

  return (
    <section id="judges" className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">Meet the Judges</h2>
          <p className="mt-4 text-xl text-violet-200">Industry experts evaluating your innovations</p>
        </div>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {judges.map((judge) => (
            <JudgeCard key={judge.name} {...judge} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default Judges;