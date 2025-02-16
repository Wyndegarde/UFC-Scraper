import { z } from "zod";

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const predictorRouter = createTRPCRouter({
    // make request to the django backend endpoint to get next event fights
  getFights: publicProcedure.query(async ({ ctx }) => {
    const response = await fetch("http://localhost:8000/predictor/next_event/");
    const data = await response.json();
    return data;
  }),
});
    
