package com.aliyun.openservices.tcp.example.consumer;
public class ByteToAscString {
    public static String bytesToAscString(byte[] src){
        StringBuilder stringBuilder = new StringBuilder("");
        if (src == null || src.length <= 0) {
            return null;
        }
        for (int i = 0; i < src.length; i++) {
            int v = src[i] & 0xFF;
            String hv = Integer.toHexString(v);
            if (hv.length() < 2) {
                stringBuilder.append(0);
            }
            stringBuilder.append(hv);
        }
        String s =stringBuilder.toString();
        byte[] messageBody = new byte[s.length() / 2];
        for (int i = 0; i < messageBody.length; i++) {
            try {
                messageBody[i] = (byte) (0xff & Integer.parseInt(s.substring(
                        i * 2, i * 2 + 2), 16));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        try {
            s = new String(messageBody, "ASCII");
        } catch (Exception e1) {
            e1.printStackTrace();
        }
        return s;
    }

}

