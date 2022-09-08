export default {
  backendUrl:
    process.env.NODE_ENV === "development" ? "http://localhost:5000" : "",
  devMode: process.env.NODE_ENV === "development",
};
