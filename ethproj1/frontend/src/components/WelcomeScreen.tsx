'use client'

import React from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit'

const WelcomeScreen = () => {
  return (
    <div className="text-center py-16">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          P2P Financial NFT Barter Exchange
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          A specialized platform for trading Financial NFTs. View real-time net values, 
          create trade listings, and execute atomic swaps directly with other DeFi strategists.
        </p>
        
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="card text-left">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Portfolio Dashboard</h3>
            <p className="text-gray-600">
              View all your Financial NFTs with real-time net value calculations from on-chain data.
            </p>
          </div>
          
          <div className="card text-left">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Atomic Swaps</h3>
            <p className="text-gray-600">
              Trade Financial NFTs and tokens safely with non-custodial atomic swap contracts.
            </p>
          </div>
          
          <div className="card text-left">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Live Valuations</h3>
            <p className="text-gray-600">
              Get accurate, real-time USD valuations of complex financial positions.
            </p>
          </div>
        </div>
        
        <div className="space-y-4">
          <p className="text-lg text-gray-700 font-medium">
            Connect your wallet to get started
          </p>
          <ConnectButton />
        </div>
        
        <div className="mt-12 text-sm text-gray-500">
          <p>
            Designed for experienced DeFi users. This is a tool-first platform for managing complex financial positions.
          </p>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen 