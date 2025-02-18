import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import type { FightDetails } from "~/types/fights";
import { env } from "~/env";

export const predictorRouter = createTRPCRouter({
    // make request to the django backend endpoint to get next event fights
  getFights: publicProcedure.query(async ({ ctx }) => {
    const baseUrl = typeof window === 'undefined' 
      ? env.BACKEND_URL 
      : env.NEXT_PUBLIC_BACKEND_URL;
      
    const response = await fetch(`${baseUrl}/predictor/predictor/`);
    if (!response.ok) {
      throw new Error('Failed to fetch fights');
    }
    const { data } = await response.json();
    return data as FightDetails[];
  }),
});
    
