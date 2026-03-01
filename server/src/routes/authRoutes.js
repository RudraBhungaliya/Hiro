import express from "express";
import passport from "passport";
import authMiddleware from "../middleware/authMiddleware.js";
import { googleCallback, getMe } from "../controllers/authController.js";

const router = express.Router();

router.get("/google",
  passport.authenticate("google", { scope: ["profile","email"] })
);

router.get("/google/callback",
  passport.authenticate("google", { session: false, failureRedirect: "/auth-failed" }),
  googleCallback
);

router.get("/me", authMiddleware, getMe);

export default router;