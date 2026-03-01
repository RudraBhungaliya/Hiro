import express from "express";
import authMiddleware from "../middleware/authMiddleware.js";
import { analyzeProject } from "../controllers/analyzeController.js";

const router = express.Router();

router.post("/", authMiddleware, analyzeProject);

export default router;