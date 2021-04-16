using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Ports;
using System.Text;
using System.Windows.Forms;

namespace UI_Skrah
{
    public partial class Manually : Form
    {
        public string pythonPath, filePath;
        public bool setHome;

        public Manually()
        {
            InitializeComponent();
            setHome = false;
        }

        private void Manually_Load(object sender, EventArgs e)
        {
            string[] ports = SerialPort.GetPortNames();
            com.Items.AddRange(ports);
        }

        public void ConnectPython()
        {
            var psi = new ProcessStartInfo();
            psi.FileName = @"C:\Anaconda3\python.exe";

            var script = @"D:\Module8-9\UI_Skrah\UI_Skrah\Resource\Protocol.py";

            if (comboBox5.Text == "joint")
            {
                if (setHome == true)
                {
                    //Set Home
                    psi.Arguments = string.Concat(script, " ", 0.ToString(), " ", 0.ToString(), " ",
                    0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ",
                    0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ",
                    0.ToString(), " ", 255.ToString(), " ", com.Text);
                }
                else
                {
                    int[] data = new int[12];

                    data[0] = 0;
                    data[1] = Convert.ToInt32(textBox1.Text);
                    data[2] = 0;
                    data[3] = Convert.ToInt32(textBox2.Text);
                    data[4] = 0;
                    data[5] = Convert.ToInt32(textBox3.Text);
                    data[6] = 0;
                    data[7] = Convert.ToInt32(textBox4.Text);
                    if (comboBox1.Text == "Left")
                        data[8] = 0;
                    else
                        data[8] = 1;
                    if (comboBox2.Text == "Up")
                        data[9] = 1;
                    else
                        data[9] = 0;
                    if (comboBox3.Text == "Left")
                        data[10] = 1;
                    else
                        data[10] = 0;
                    if (comboBox4.Text == "Off")
                        data[11] = 0;
                    else
                        data[11] = 1;

                    for (int i = 0; i < 8; i++)
                    {
                        if (data[i] > 255)
                        {
                            int s = 0;
                            s = data[i] / 256;
                            data[i] = data[i] % 256;
                            data[i - 1] = s;
                        }
                    }

                    psi.Arguments = string.Concat(script, " ", data[0].ToString(), " ", data[1].ToString(), " ",
                    data[2].ToString(), " ", data[3].ToString(), " ", data[4].ToString(), " ", data[5].ToString(), " ",
                    data[6].ToString(), " ", data[7].ToString(), " ", data[8].ToString(), " ", data[9].ToString(), " ",
                    data[10].ToString(), " ", data[11].ToString(), " ", com.Text);
                }
                
            }

            if (comboBox5.Text == "cartesian")
            {
                if (setHome == true)
                {
                    //Set Home
                    psi.Arguments = string.Concat(script, " ", 0.ToString(), " ", 0.ToString(), " ",
                    0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ",
                    0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ", 0.ToString(), " ",
                    0.ToString(), " ", 255.ToString(), " ", com.Text);
                }
                else
                {
                    int d1 = Convert.ToInt32(textBox7.Text);
                    int d2 = Convert.ToInt32(textBox6.Text);
                    int d3 = Convert.ToInt32(textBox5.Text);
                    int d4 = Convert.ToInt32(comboBox6.Text);
                    int d5 = 0;

                    if (comboBox4.Text == "Off")
                        d5 = 0;
                    else
                        d5 = 1;

                    psi.Arguments = string.Concat(script, " ", d1.ToString(), " ", d2.ToString(), " ",
                    d3.ToString(), " ", d4.ToString(), " ", d5.ToString(), " ", com.Text);
                }
                
            }

            

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
                if (results[i] == '!')
                {
                    progressBar1.Value = 100;
                    setHome = false;
                }
            }

        }

        private void run_Click(object sender, EventArgs e)
        {
            progressBar1.Value = 0;
            ConnectPython();
            //Console.WriteLine(comboBox5.Text);
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

        private void button1_Click(object sender, EventArgs e)
        {
            OpenFileDialog pyPath = new OpenFileDialog();
            if (pyPath.ShowDialog() == DialogResult.OK)
            {
                pythonPath = pyPath.FileName;
                MessageBox.Show(pythonPath);
            }
        }

        private void button1_Click_1(object sender, EventArgs e)
        {
            progressBar1.Value = 0;
            setHome = true;
            ConnectPython();
        }

        private void button1_MouseDown(object sender, MouseEventArgs e)
        {
            button1.BackColor = Color.Black;
        }

        private void button1_MouseUp(object sender, MouseEventArgs e)
        {
            button1.BackColor = Color.FromArgb(121, 85, 72);
        }

        private void run_MouseDown(object sender, MouseEventArgs e)
        {
            run.BackColor = Color.Black;
        }

        private void run_MouseUp(object sender, MouseEventArgs e)
        {
            run.BackColor = Color.FromArgb(0, 137, 123);
        }

        private void comboBox5_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (comboBox5.Text == "joint")
            {
                label7.Visible = false;
                label8.Visible = false;
                label9.Visible = false;
                label11.Visible = false;
                textBox5.Visible = false;
                textBox6.Visible = false;
                textBox7.Visible = false;
                comboBox6.Visible = false;

                label2.Visible = true;
                label3.Visible = true;
                label4.Visible = true;
                label5.Visible = true;
                textBox1.Visible = true;
                textBox2.Visible = true;
                textBox3.Visible = true;
                textBox4.Visible = true;
                comboBox1.Visible = true;
                comboBox2.Visible = true;
                comboBox3.Visible = true;
            }
            if (comboBox5.Text == "cartesian")
            {
                label7.Visible = true;
                label8.Visible = true;
                label9.Visible = true;
                label11.Visible = true;
                textBox5.Visible = true;
                textBox6.Visible = true;
                textBox7.Visible = true;
                comboBox6.Visible = true;

                label2.Visible = false;
                label3.Visible = false;
                label4.Visible = false;
                label5.Visible = false;
                textBox1.Visible = false;
                textBox2.Visible = false;
                textBox3.Visible = false;
                textBox4.Visible = false;
                comboBox1.Visible = false;
                comboBox2.Visible = false;
                comboBox3.Visible = false;
            }
        }

    }
}
