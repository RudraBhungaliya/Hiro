import mongoose from "mongoose";

const historySchema = new mongoose.Schema({
  userId: String,
  repoPath: String,
  mermaid: String,
  description: String,
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model("History", historySchema);