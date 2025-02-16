"use client";


import type { FightsProps } from "~/types/fights";

export function Fights({ fights }: FightsProps) {
  return (
    <div>
      {fights.map((fight) => (
        <div key={fight.red_fighter}>{fight.red_fighter}</div>
      ))}
    </div>
  );
}
