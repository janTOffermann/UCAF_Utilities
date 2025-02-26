#!/cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/bin/python
# Author: Jan T. Offermann

import sys,os,datetime,glob,pathlib,re
import argparse as ap
import numpy as np
import ROOT as rt

def GetClusterAndJobName(lines):
    key_phrase = 'Job submitted from host'
    for line in lines:
        if(key_phrase in line):
            return line.split(')')[0].split('(')[-1].strip()
    return 'NONE'

def TextLinesToTimestamps(timestamp_lines,format='%Y-%m-%d %H:%M:%S'):
    lines = [' '.join(x.split(' ')[2:4]).strip() for x in timestamp_lines]
    return np.array([float(datetime.datetime.strptime(x,format).strftime('%s')) for x in lines])

def GetAllTimestamps(lines,format='%Y-%m-%d %H:%M:%S'):
    regex = '^[0-9]{3} \('
    matches = []
    for line in lines:
        match = re.findall(regex,line)
        if(len(match) > 0): matches.append(line)
    return TextLinesToTimestamps(matches,format)

def GetExecutionStartTimestamp(lines,format='%Y-%m-%d %H:%M:%S'):
    key_phrase = 'Job executing on host'
    for line in lines:
        if(key_phrase in line):
            return TextLinesToTimestamps([line])[0]
    return -999

def GetInfo(lines,key_phrase='Job was held.',info_type='Hold',format='%Y-%m-%d %H:%M:%S',get_info=True, time_offset=0.):
    times = []
    infos = []
    for i,line in enumerate(lines):
        if(key_phrase in line):
            times.append(line)
            if(get_info):
                try: infos.append('({}, {}) ' + lines[i+1])
                except: infos.append('({}, {})' + ' Error: {} info not found!'.format(info_type))
            else:
                infos.append('')
    times = [x.split(key_phrase)[0].split(')')[-1].strip() for x in times]
    for i in range(len(times)):
        infos[i] = infos[i].format(info_type,times[i])
    times = np.array([float(datetime.datetime.strptime(x,format).strftime('%s')) for x in times]) + time_offset
    return times, infos

def DrawLines(times,infos,ymax=10.,color=rt.kRed,text_size=0.015,alpha=1.,x_offset=0.,canvas=None):
    lines = []
    texts = []
    if(canvas is not None): canvas.cd()
    for j,hold in enumerate(times):
        # Draw a vertical line indicating the time of the hold.
        hold_line = rt.TLine(hold,0.,hold,ymax)
        hold_line.SetLineColorAlpha(color,alpha)
        hold_line.SetLineWidth(2)
        hold_line.SetLineStyle(2)
        hold_line.Draw()
        lines.append(hold_line)

        # Add some text to explain the hold line.
        hold_text = rt.TText(hold + x_offset,ymax/2.,infos[j])
        hold_text.SetTextAlign(23)
        hold_text.SetTextColor(color)
        hold_text.SetTextFont(43)
        hold_text.SetTextSize(text_size)
        hold_text.SetTextAngle(90)
        hold_text.Draw()
        texts.append(hold_text)
    return lines,texts

def main(args):
    parser = ap.ArgumentParser()
    parser.add_argument('-i','--input',type=str, required=True,help='Glob-compatible string for filename(s).')
    parser.add_argument('-o','--outdir',type=str, default=None,help='Output directory for plots.')
    parser.add_argument('-f','--force',type=int,default=0,help='Whether or not to force output.')
    args = vars(parser.parse_args())

    inputs = glob.glob(args['input'])
    inputs.sort()
    outdir = args['outdir']
    force = args['force'] > 0
    if(outdir is None): outdir = os.getcwd()
    os.makedirs(outdir,exist_ok=True)

    print("\tInputs = ")
    for f in inputs:
        print('\t\t{}'.format(f))

    output_file = '{}/condor_memory.root'.format(outdir)
    if(pathlib.Path(output_file).exists() and not force):
        print('\tError: Output file {} already exists. We don\'t want to accidentally overwrite something -> exiting.'.format(output_file))
        return

    rt.gStyle.SetOptStat(0)

    canvases = []
    graphs = []
    hists = []
    lines = []
    texts = []
    for i,input in enumerate(inputs):
        with open(input,"r") as f:
            log_lines = f.readlines()

        key_phrase = 'MemoryUsage of job (MB)'
        mem_lines = [x for x in log_lines if key_phrase in x]
        memory = np.array([float(x.split('-')[0].strip()) for x in mem_lines])
        memory /= 1024.

        timestamps = GetAllTimestamps(log_lines)
        min_time = GetExecutionStartTimestamp(log_lines)
        max_time = np.max(timestamps)
        dtime = max_time - min_time

        key_phrase = 'Image size of job updated'
        format = '%Y-%m-%d %H:%M:%S'
        time_lines = [x for x in log_lines if key_phrase in x]
        times = [x.split(key_phrase)[0].split(')')[-1].strip() for x in time_lines]
        times = np.array([float(datetime.datetime.strptime(x,format).strftime('%s')) for x in times])
        times = (times - min_time) / 3600. # converting to duration, in hours, since starting job execution

        canvas_name = 'c_{}'.format(GetClusterAndJobName(log_lines))
        canvas_dims = (800,600)
        c = rt.TCanvas(canvas_name,canvas_name,*canvas_dims)
        rt.gPad.SetTopMargin(0.05)
        rt.gPad.SetRightMargin(0.05)
        rt.gPad.SetBottomMargin(0.15)

        g = rt.TGraph()
        g.SetName("graph_{}".format(i))
        for j,x in enumerate(times):
            g.AddPoint(x,memory[j])

        g.Draw("ALP")
        ymax = g.GetHistogram().GetMaximum()

        n_dummy = 10
        dummy_hist = rt.TH1I('dummy_hist_{}'.format(i),'',n_dummy,0.,(1.05 * dtime) / 3600.)
        for i in range(n_dummy):
            dummy_hist.SetBinContent(i+1,0.)
        dummy_hist.Draw('HIST')
        dummy_hist.SetMaximum(ymax)
        # dummy_hist.GetXaxis().SetTimeDisplay(1)
        # dummy_hist.GetXaxis().SetTimeFormat("%Y-%m-%d,  %H:%M:%S")
        # dummy_hist.GetXaxis().SetTimeOffset(0,'gmt')
        dummy_hist.GetXaxis().SetLabelSize(0.03)
        dummy_hist.GetXaxis().SetTitle('Duration [Hours]')
        dummy_hist.GetYaxis().SetTitle('Memory [GB]')
        dummy_hist.SetTitle(input)

        g.Draw("LP SAME")
        #c.Draw()

        g.SetLineColor(rt.kBlue)
        g.SetLineWidth(2)
        g.SetMarkerStyle(rt.kFullCircle)
        g.SetMarkerColor(rt.kBlue)

        rt.gPad.SetGrid()

        # Also, we will decorate the plot with some additional info on what the jobs were doing.
        holds,hold_infos = GetInfo(log_lines,key_phrase='Job was held.',info_type='Hold',format=format, time_offset=-min_time)
        holds /= 3600.
        x_offset = 0.0025 * dtime / 3600.
        hold_lines,hold_texts = DrawLines(holds, hold_infos,ymax,x_offset=x_offset)

        releases,releases_infos = GetInfo(log_lines,key_phrase='Job was released.',info_type='Release',format=format, time_offset=-min_time)
        releases /= 3600.
        release_lines,release_texts = DrawLines(releases, releases_infos,ymax,x_offset=x_offset,color=rt.kGreen+2)

        evictions,evictions_infos = GetInfo(log_lines,key_phrase='Job was evicted.',info_type='Eviction',format=format,get_info=False, time_offset=-min_time)
        evictions /= 3600.
        abortions,abortions_infos = GetInfo(log_lines,key_phrase='Job was aborted.',info_type='Abort',   format=format, time_offset=-min_time)
        abortions /= 3600.

        # There will be some overlap of evictions and abortions, so let us remove it.
        try:
            intersect = np.concatenate([np.where(evictions == x)[0] for x in np.intersect1d(evictions,abortions)])
            evictions[intersect] = -999. # will be off the plot
        except:
            pass

        eviction_lines,eviction_texts = DrawLines(evictions, evictions_infos,ymax,x_offset=x_offset,color=rt.kBlack)
        abortion_lines,abortion_texts = DrawLines(abortions, abortions_infos,ymax,x_offset=x_offset,color=rt.kBlack)

        c.Draw()
        canvases.append(c)
        graphs.append(g)
        hists.append(dummy_hist)
        lines.append([hold_lines,release_lines,abortion_lines,eviction_lines])
        texts.append([hold_texts,release_texts,abortion_texts,eviction_texts])

    f = rt.TFile(output_file,'RECREATE')
    for i,c in enumerate(canvases):
        c.Write()
        # c.SaveAs("{}/plot_{}.pdf".format(outdir,i))
    f.Close()

if(__name__=='__main__'):
    main(sys.argv)
