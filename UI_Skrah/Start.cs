using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace UI_Skrah
{
    public partial class Start : Form
    {
        public Button[] button = new Button[15];
        public string box;
        public bool check;

        public Start()
        {
            InitializeComponent();
            check = false;

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
            //Decode.Print();
            Visible_Buttons();
            this.Invalidate();     
        }

        private void Visible_Buttons()
        {
            foreach (KeyValuePair<int, string> kvp in Decode.dictBox)
            {
                Console.WriteLine("Key = {0}, Value = {1}",
                                  kvp.Key, kvp.Value);
                button[kvp.Key].Text = kvp.Value;
                button[kvp.Key].BackColor = Color.Red;
            }
            //for (int i = 1; i <= 14; i++)
            //{
            //    button[i].BackColor = Color.Red;
            //}
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

        private void run_Click(object sender, EventArgs e)
        {
            if (textBox1.Text.Length > 0)
            {
                FindBox();
                if (check == true)
                {
                    AutoRun();
                }
            }
            else
            {
                AutoRun();
            }
        }

        public void FindBox()
        {
            var psi = new ProcessStartInfo();
            psi.FileName = @"C:\Anaconda3\python.exe";

            var script = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource\search-fuzzy.py";

            psi.WorkingDirectory = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource";


            psi.Arguments = string.Concat(script, " ", textBox1.Text);

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
                if (results[i] == 'x')
                {
                    check = true;
                    if (results.Length > 4)
                        box = Char.ToString(results[i + 1]) + Char.ToString(results[i + 2]);
                    else
                        box = Char.ToString(results[i + 1]);
                    int x = 0;
                    Int32.TryParse(box, out x);
                    button[x].BackColor = Color.FromArgb(63, 81, 181);
                }
            }

            Debug.WriteLine(box);
            
        }

        public void AutoRun()
        {
            var psi = new ProcessStartInfo();
            psi.FileName = @"C:\Anaconda3\python.exe";

            var script = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource\send.py";

            //psi.Arguments = string.Concat(script, " ", box);
            if (textBox1.Text.Length > 0)
            {
                psi.Arguments = string.Concat(script, " ", 254, " ", box);
            }
            else
            {
                foreach (KeyValuePair<int, string> kvp in Decode.dictOut)
                {
                    psi.Arguments = string.Concat(script, " ", 254, " ", kvp.Key);
                    Debug.WriteLine(kvp.Key);
                }
            }

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

            //for (int i = 0; i < results.Length; i++)
            //{
            //    if (results[i] == '!')
            //    {
            //        check = false;
            //        MessageBox.Show("Successed!");
            //    }
            //}

        }

        private void run_MouseDown(object sender, MouseEventArgs e)
        {
            run.BackColor = Color.Black;
        }

        private void run_MouseUp(object sender, MouseEventArgs e)
        {
            run.BackColor = Color.FromArgb(0, 137, 123);
        }

        private void button1_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(1, "Box1");
            button1.BackColor = Color.Red;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(2, "Box2");
            button2.BackColor = Color.Red;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(3, "Box3");
            button3.BackColor = Color.Red;
        }

        private void button4_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(4, "Box4");
            button4.BackColor = Color.Red;
        }

        private void button5_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(5, "Box5");
            button5.BackColor = Color.Red;
        }

        private void button6_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(6, "Box6");
            button6.BackColor = Color.Red;
        }

        private void button7_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(7, "Box7");
            button7.BackColor = Color.Red;
        }

        private void button8_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(8, "Box8");
            button8.BackColor = Color.Red;
        }

        private void button9_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(9, "Box9");
            button9.BackColor = Color.Red;
        }

        private void button10_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(10, "Box10");
            button10.BackColor = Color.Red;
        }

        private void button11_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(11, "Box11");
            button11.BackColor = Color.Red;
        }

        private void button12_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(12, "Box12");
            button12.BackColor = Color.Red;
        }

        private void button13_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(13, "Box13");
            button13.BackColor = Color.Red;
        }

        private void button14_Click(object sender, EventArgs e)
        {
            Decode.dictOut.Add(14, "Box14");
            button14.BackColor = Color.Red;
        }
    }
}
