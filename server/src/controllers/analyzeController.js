import axios from "axios";
import History from "../models/History.js";

export const analyzeProject = async (req, res) => {
  try {
    const { path } = req.body;

    if (!path) {
      return res.status(400).json({ error: "Path is required" });
    }

    console.log("📡 Calling Python AI service...");

    // call python AI service
    const aiResponse = await axios.post("http://localhost:9000/analyze", {
      path,
    });

    const result = aiResponse.data;

    console.log("✅ AI response received");

    const repoName= path.split("/").slice(-1)[0];

    // save history in MongoDB
    await History.create({
      userId: req.userId,
      repoPath: repoName,
      mermaid: result.mermaid,
      description: result.description,
      createdAt: new Date(),
    });

    res.json(result);

  } catch (error) {
    console.error("❌ Analyze error:", error.message);
    res.status(500).json({ error: "Analysis failed" });
  }
};