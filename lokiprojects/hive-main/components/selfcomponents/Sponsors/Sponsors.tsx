import React from 'react';

const Sponsors = () => {
  const sponsors = [
    { name: 'Ethereum', logo: 'https://cryptologos.cc/logos/ethereum-eth-logo.png' },
    { name: 'Polygon', logo: 'https://cryptologos.cc/logos/polygon-matic-logo.png' },
    { name: 'Binance', logo: 'https://cryptologos.cc/logos/binance-coin-bnb-logo.png' },
    { name: 'Chainlink', logo: 'https://cryptologos.cc/logos/chainlink-link-logo.png' },
    { name: 'Solana', logo: 'https://cryptologos.cc/logos/solana-sol-logo.png' },
    { name: 'Avalanche', logo: 'https://cryptologos.cc/logos/avalanche-avax-logo.png' },
    { name: 'Cardano', logo: 'https://cryptologos.cc/logos/cardano-ada-logo.png' },
    { name: 'Polkadot', logo: 'https://cryptologos.cc/logos/polkadot-new-dot-logo.png' },
    { name: 'Cosmos', logo: 'https://cryptologos.cc/logos/cosmos-atom-logo.png' },
    { name: 'Near', logo: 'https://cryptologos.cc/logos/near-protocol-near-logo.png' },
    { name: 'Algorand', logo: 'https://cryptologos.cc/logos/algorand-algo-logo.png' },
    { name: 'Tezos', logo: 'https://cryptologos.cc/logos/tezos-xtz-logo.png' },
    { name: 'Fantom', logo: 'https://cryptologos.cc/logos/fantom-ftm-logo.png' },
    { name: 'Hedera', logo: 'https://cryptologos.cc/logos/hedera-hbar-logo.png' },
    { name: 'Filecoin', logo: 'https://cryptologos.cc/logos/filecoin-fil-logo.png' },
  ];

  return (
    <section id="sponsors" className="relative py-24 bg-black overflow-hidden">
      <div className="stars-1"></div>
      <div className="stars-2"></div>
      <div className="stars-3"></div>
      <div className="relative z-10">
        <h2 className="section-heading text-center mb-16">Our Sponsors</h2>
        <div className="relative overflow-hidden">
          <div className="flex animate-scroll">
            {[...sponsors, ...sponsors].map((sponsor, index) => (
              <div
                key={index}
                className="flex-none w-48 h-24 mx-8 flex items-center justify-center"
              >
                <img
                  src={sponsor.logo}
                  alt={sponsor.name}
                  className="max-w-[120px] max-h-[60px] object-contain filter brightness-0 invert opacity-60 hover:opacity-100 transition-opacity"
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export default Sponsors;