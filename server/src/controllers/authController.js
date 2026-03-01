import jwt from "jsonwebtoken";
import User from "../models/User.js";

export const googleCallback = (req, res) => {
  const token = jwt.sign(
    { id: req.user._id },
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );

  const frontendUrl = process.env.FRONTEND_URL || "http://localhost:5174";
  res.redirect(`${frontendUrl}/login-success?token=${token}`);
};

export const getMe = async (req, res) => {
  try {
    const user = await User.findById(req.userId).select("name email picture").lean();
    if (!user) return res.status(404).json({ error: "User not found" });
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: "Failed to load user" });
  }
};