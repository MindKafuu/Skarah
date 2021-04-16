using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Timers;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using HDF5DotNet;

namespace UI_Skrah
{
    public partial class Receive : Form
    {
        public bool check, chk, next, capture;
        public int randBox, count;
        public Button[] button = new Button[15];
        public List<int> checkBox = new List<int>() { 7, 8, 9, 10, 11, 12, 13, 14, 6, 5, 4, 3, 2, 1 };
        public Dictionary<int, string> traject = new Dictionary<int, string>()
        {
            {1,"Box1"}, {2,"Box2"}, {3,"Box3"}, {4,"Box4"}, {5,"Box5"}, {6,"Box6"}, {7,"Box7"},
            {8,"Box8"}, {9,"Box9"}, {10,"Box10"}, {11,"Box11"}, {12,"Box12"}, {13,"Box13"},{14,"Box14"},
        };

        public Receive()
        {
            InitializeComponent();
            //ConnectPython();
            count = 0;
            check = false;
            chk = false;
            next = false;
            capture = false;
            Decode.dict.Clear();
            Decode.dictBox.Clear();
            button[0] = null;
            button[1] = button1;
            button[2] = button2;
            button[3] = button3;
            button[4] = button4;
            button[5] = button5;
            button[6] = button6;
            button[7] = button7;
            button[8] = button8;
            button[9] = button9;
            button[10] = button10;
            button[11] = button11;
            button[12] = button12;
            button[13] = button13;
            button[14] = button14;


        }

        public void Visible_button()
        {
            for (int i = 1; i <= 14; i++)
            {
                button[i].BackColor = Color.FromArgb(63, 81, 181);
                button[i].Enabled = true;
            }
        }

        public void ConnectPython()
        {
            var psi = new ProcessStartInfo();
            psi.FileName = @"C:\Anaconda3\python.exe";

            var script = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource\magic-code.py";
            psi.WorkingDirectory = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource";

            psi.Arguments = string.Concat(script, " ", randBox);

            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;

            var errors = "";
            var results = "";

            using (var process = Process.Start(psi))
            {
                errors = process.StandardError.ReadToEnd();
                results = process.StandardOutput.ReadToEnd();
            }

            Console.WriteLine("ERRORS:");
            Debug.WriteLine(errors);
            Console.WriteLine();
            Console.WriteLine("Results:");
            Debug.WriteLine(results);


            for (int i = 0; i < results.Length; i++)
            {
                if (results[i] == 'E')
                {
                    check = true;
                }

            }

        }

            private void pictureBox1_Click(object sender, EventArgs e)
        {
            this.Close();
            Form1 main = new Form1();
            main.Show();
        }

        private void pictureBox2_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

        public void ConnectPython1()
        {
            Debug.WriteLine(check);
            var psi = new ProcessStartInfo();
            psi.FileName = @"C:\Anaconda3\python.exe";

            var script = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource\Resource\test29.py";
            psi.Arguments = string.Concat(script, " ", randBox);


            psi.WorkingDirectory = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource";

            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;

            var errors = "";
            var results = "";

            using (var process = Process.Start(psi))
            {
                errors = process.StandardError.ReadToEnd();    
                results = process.StandardOutput.ReadToEnd();
            }

            Debug.WriteLine("ERRORS:");
            Debug.WriteLine(errors);
            Debug.WriteLine("\n");
            Debug.WriteLine("Results:");
            Debug.WriteLine(results);

            for (int i = 0; i < results.Length; i++)
            {
                if (results[i] == 'E')
                {
                    Decode read = new Decode();
                    textBox1.Text = read.ReadFile();
                    Decode.dictBox.Add(randBox, textBox1.Text);

                    chk = false;
                }

            }

        }

        private void button1_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(1, "Box1");
            button1.BackColor = Color.Red;
            //Decode.dictBox.Add(1, textBox1.Text);
            button1.Enabled = false;
        }
        private void button2_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(2, "Box2");
            button2.BackColor = Color.Red;
            Decode.dictBox.Add(2, "นนทพัตน์-47/71 วันดี");
            button2.Enabled = false;
        }
        private void button3_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(3, "Box3");
            button3.BackColor = Color.Red;
            //Decode.dictBox.Add(3, textBox1.Text);
            button3.Enabled = false;
        }

        private void cap_Click(object sender, EventArgs e)
        {
            this.Invalidate();
            if (checkBox1.CheckState == CheckState.Checked)
            {
                if (checkBox2.CheckState == CheckState.Checked)
                {
                    foreach (KeyValuePair<int, string> kvp in Decode.dict)
                    {
                        Console.WriteLine("Key = {0}, Value = {1}",
                                          kvp.Key, kvp.Value);
                        randBox = kvp.Key;
                    }
                    Debug.WriteLine(randBox);

                    ConnectPython();
                    if (check == true)
                    {
                        AutoRun();
                        if (chk == true)
                        {
                            ConnectPython1();
                        }
                    }
                }
                else
                {
                    foreach (KeyValuePair<int, string> kvp in Decode.dict)
                    {
                        Console.WriteLine("Key = {0}, Value = {1}",
                                          kvp.Key, kvp.Value);
                        randBox = kvp.Key;
                    }
                    AutoRun();
                }
            }
            else
            {
                capture = true;
                foreach (KeyValuePair<int, string> kvp in Decode.dict)
                {
                    Console.WriteLine("Key = {0}, Value = {1}",
                                      kvp.Key, kvp.Value);
                    checkBox.Remove(kvp.Key);
                }

                for (int i = 0; i < 5; i++)
                {
                    if (capture == true)
                    {
                        Debug.WriteLine(checkBox[i]);
                        randBox = checkBox[i];
                        Decode.dict.Add(randBox, traject[randBox]);

                        button[randBox].BackColor = Color.Red;
                        button[randBox].Enabled = false;

                        ConnectPython();
                        if (check == true)
                        {
                            AutoRun();
                            if (chk == true)
                            {
                                ConnectPython1();
                            }
                        }
                    }

                }
                capture = false;
            }

        }

        public void AutoRun()
        {
            var psi = new ProcessStartInfo();
            psi.FileName = @"C:\Anaconda3\python.exe";

            var script = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource\send.py";

            psi.Arguments = string.Concat(script, " ", 253, " ", randBox);

            psi.WorkingDirectory = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource";

            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;

            var errors = "";
            var results = "";

            using (var process = Process.Start(psi))
            {
                errors = process.StandardError.ReadToEnd();
                results = process.StandardOutput.ReadToEnd();
            }

            Console.WriteLine("ERRORS:");
            Console.WriteLine(errors);
            Console.WriteLine();
            Console.WriteLine("Results:");
            Console.WriteLine(results);

            for (int i = 0; i < results.Length; i++)
            {
                if (results[i] == 'E')
                {
                    chk = true;
                }
            }

        }

        private void button4_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(4, "Box4");
            button4.BackColor = Color.Red;
            //Decode.dictBox.Add(4, textBox1.Text);
            button4.Enabled = false;
        }

        private void button5_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(5, "Box5");
            button5.BackColor = Color.Red;
            //Decode.dictBox.Add(5, textBox1.Text);
            button5.Enabled = false;
        }

        private void button6_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(6, "Box6");
            button6.BackColor = Color.Red;
            //Decode.dictBox.Add(6, textBox1.Text);
            button6.Enabled = false;
        }

        private void button7_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(7, "Box7");
            button7.BackColor = Color.Red;
            //Decode.dictBox.Add(7, textBox1.Text);
            button7.Enabled = false;
        }

        private void button8_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(8, "Box8");
            button8.BackColor = Color.Red;
            //Decode.dictBox.Add(8, textBox1.Text);
            button8.Enabled = false;
        }

        private void button9_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(9, "Box9");
            button9.BackColor = Color.Red;
            //Decode.dictBox.Add(9, "น้องวันโรโบติก");
            button9.Enabled = false;
        }

        private void button10_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(10, "Box10");
            button10.BackColor = Color.Red;
            //Decode.dictBox.Add(10, textBox1.Text);
            button10.Enabled = false;
        }

        private void button11_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(11, "Box11");
            button11.BackColor = Color.Red;
            //Decode.dictBox.Add(11, textBox1.Text);
            button11.Enabled = false;
        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {
            Visible_button();
        }


        private void button12_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(12, "Box12");
            button12.BackColor = Color.Red;
            //Decode.dictBox.Add(12, "นนธพัต");
            button12.Enabled = false;
        }

        private void button13_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(13, "Box13");
            button13.BackColor = Color.Red;
            //Decode.dictBox.Add(13, textBox1.Text);
            button13.Enabled = false;
        }

        private void button14_Click(object sender, EventArgs e)
        {
            Decode.dict.Add(14, "Box14");
            button14.BackColor = Color.Red;
            Decode.dictBox.Add(14, "สงกรานต์-83/71 ตำบลหัวรอ อำเภอเมือง จังหวัดพิษณุโลก");
            button14.Enabled = false;
        }
    }
}
