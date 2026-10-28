import { useAuth } from "../../context/AuthContext";
export const usePermissions = () => {
  const { user } = useAuth();


  console.log("🔄 usePermissions - user recebido:", user);
  console.log("🔄 usePermissions - role do user:", user?.role);

  const isAdmin = user?.role === "ADMIN";
  const isUser = user?.role === "USER";

  console.log("🔄 usePermissions - isAdmin:", isAdmin);

  return {
    isAdmin,
    isUser,
    role: user?.role || null,
  };
};
