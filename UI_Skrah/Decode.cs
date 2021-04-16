using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UI_Skrah
{
    public class Decode
    {
        public static Dictionary<int, string> dict = new Dictionary<int, string>();
        public static Dictionary<int, string> dictBox = new Dictionary<int, string>();
        public static Dictionary<int, string> dictOut = new Dictionary<int, string>();

        public string ReadFile()
        {
            string text;
            var fileStream = new FileStream(@"D:\Work-3.2\GUI\UI_Skrah\UI_Skrah\Resource\testfile.txt", FileMode.Open, FileAccess.Read);
            using (var streamReader = new StreamReader(fileStream, Encoding.UTF8))
            {
                text = streamReader.ReadToEnd();
            }

            return text;
        }
    }
}
