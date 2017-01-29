﻿using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
//using System.Diagnostics;

namespace Common.Cryptography
{
    /// <summary>
    /// AES is a symmetric 256-bit encryption algorthm.
    /// Read more: http://en.wikipedia.org/wiki/Advanced_Encryption_Standard
    /// </summary>
    public static class AES
    {
        private const string _SALT = "g46dzQ80";				// Salt to encrypt with
        private const string _INITVECTOR = "OFRna74m*aze01xY";	// Needs to be 16 ASCII characters long

        private static byte[] _saltBytes;
        private static byte[] _initVectorBytes;

        static AES()
        {
            _saltBytes = Encoding.UTF8.GetBytes(_SALT);
            _initVectorBytes = Encoding.UTF8.GetBytes(_INITVECTOR);
        }


        /// <summary>
        /// Encrypts a string with AES
        /// </summary>
        /// <param name="plainText">Text to be encrypted</param>
        /// <param name="password">Password to encrypt with</param>
        /// <returns>An encrypted string</returns>
        public static string Encrypt(string plainText, string password)
        {
            return Convert.ToBase64String(EncryptToBytes(plainText, password, _SALT, _INITVECTOR));
        }

        /// <summary>
        /// Encrypts a string with AES
        /// </summary>
        /// <param name="plainText">Text to be encrypted</param>
        /// <param name="password">Password to encrypt with</param>
        /// <param name="salt">Salt to encrypt with</param>
        /// <param name="initialVector">Needs to be 16 ASCII characters long</param>
        /// <returns>An encrypted string</returns>
        public static byte[] EncryptToBytes(string plainText, string password, string salt = null, string initialVector = null)
        {
            byte[] plainTextBytes = Encoding.UTF8.GetBytes(plainText);
            return EncryptToBytes(plainTextBytes, password, salt, initialVector);
        }

        /// <summary>
        /// Encrypts a string with AES
        /// </summary>
        /// <param name="plainTextBytes">Bytes to be encrypted</param>
        /// <param name="password">Password to encrypt with</param>
        /// <param name="salt">Salt to encrypt with</param>
        /// <param name="initialVector">Needs to be 16 ASCII characters long</param>
        /// <returns>An encrypted string</returns>
        public static byte[] EncryptToBytes(byte[] plainTextBytes, string password, string salt = null, string initialVector = null)
        {
            int keySize = 256;

            byte[] initialVectorBytes = string.IsNullOrEmpty(initialVector) ? _initVectorBytes : Encoding.UTF8.GetBytes(initialVector);
            byte[] saltValueBytes = string.IsNullOrEmpty(salt) ? _saltBytes : Encoding.UTF8.GetBytes(salt);
            byte[] keyBytes = new Rfc2898DeriveBytes(password, saltValueBytes).GetBytes(keySize / 8);

            using (RijndaelManaged symmetricKey = new RijndaelManaged())
            {
                symmetricKey.Mode = CipherMode.CBC;

                using (ICryptoTransform encryptor = symmetricKey.CreateEncryptor(keyBytes, initialVectorBytes))
                {
                    using (MemoryStream memStream = new MemoryStream())
                    {
                        using (CryptoStream cryptoStream = new CryptoStream(memStream, encryptor, CryptoStreamMode.Write))
                        {
                            cryptoStream.Write(plainTextBytes, 0, plainTextBytes.Length);
                            cryptoStream.FlushFinalBlock();

                            return memStream.ToArray();
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Decrypts an AES-encrypted string.
        /// </summary>
        /// <param name="cipherText">Text to be decrypted</param>
        /// <param name="password">Password to decrypt with</param>
        /// <returns>A decrypted string</returns>
        public static string Decrypt(string cipherText, string password)
        {
            byte[] cipherTextBytes = Convert.FromBase64String(cipherText.Replace(' ','+'));
            return Decrypt(cipherTextBytes, password, _SALT, _INITVECTOR).TrimEnd('\0');
        }

        /// <summary>
        /// Decrypts an AES-encrypted string.
        /// </summary>
        /// <param name="cipherTextBytes">Text to be decrypted</param>
        /// <param name="password">Password to decrypt with</param>
        /// <param name="salt">Salt to decrypt with</param>
        /// <param name="initialVector">Needs to be 16 ASCII characters long</param>
        /// <returns>A decrypted string</returns>
        public static string Decrypt(byte[] cipherTextBytes, string password, string salt = null, string initialVector = null)
        {
            int keySize = 256;

            byte[] initialVectorBytes = string.IsNullOrEmpty(initialVector) ? _initVectorBytes : Encoding.UTF8.GetBytes(initialVector);
            byte[] saltValueBytes = string.IsNullOrEmpty(salt) ? _saltBytes : Encoding.UTF8.GetBytes(salt);
            byte[] keyBytes = new Rfc2898DeriveBytes(password, saltValueBytes).GetBytes(keySize / 8);
            byte[] plainTextBytes = new byte[cipherTextBytes.Length];

            using (RijndaelManaged symmetricKey = new RijndaelManaged())
            {
                symmetricKey.Mode = CipherMode.CBC;

                using (ICryptoTransform decryptor = symmetricKey.CreateDecryptor(keyBytes, initialVectorBytes))
                {
                    using (MemoryStream memStream = new MemoryStream(cipherTextBytes))
                    {
                        using (CryptoStream cryptoStream = new CryptoStream(memStream, decryptor, CryptoStreamMode.Read))
                        {
                            int byteCount = cryptoStream.Read(plainTextBytes, 0, plainTextBytes.Length);

                            return Encoding.UTF8.GetString(plainTextBytes, 0, byteCount);
                        }
                    }
                }
            }
        }
    }
}