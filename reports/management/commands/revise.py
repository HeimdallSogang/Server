from django.core.management.base import BaseCommand, CommandError

from reports.models import Point, Report
from test_code.analyze import analyze, read_pdf

class Command(BaseCommand):
    help = "Revise points or analyst names on a report"

    def add_arguments(self, parser):
        target_choices = ["point", "analyst"]
        parser.add_argument(
            "target", 
            choices=target_choices,
            type=str,
            help=f"What to revise. Select between {target_choices}",
        )
        parser.add_argument(
            "report_title",
            type=str,
            help='(Partial) title of report to revise. Example: "수익성 하락과 경쟁 압력에"',
        )

    def handle(self, *args, **options):
        revise_target = options["target"]
        report_title = options["report_title"]

        # get report object
        report_candidates = Report.objects.filter(title__icontains=report_title)
        report = None
        if len(report_candidates) == 0:
            raise CommandError(f"No report with title that contains {report_title}")
        elif len(report_candidates) > 1:
            for (idx, rc) in enumerate(report_candidates):
                print(f"{idx}: {rc.title:<20} {rc.publish_date}")
            
            print("Select report number you are referring to")
            report_idx = input(">> ")
            try: 
                report_idx = int(report_idx)
                if report_idx < 0 or report_idx >= len(report_candidates):
                    raise ValueError()
            except (ValueError, TypeError):
                raise CommandError("Input a valid index")
            
            report = report_candidates[idx]
        else:
            report = report_candidates[0]
        
        if revise_target == "point":
            # display existing points
            print("List point numbers to DELETE with whitespace in between. Type 'a' for all points.")
            print(f"Reference to the original report: {report.url}")

            points = Point.objects.filter(report=report)
            for (idx, point) in enumerate(points):
                print(f"{idx}: {point.content}")
            
            # input existing points index to discard
            discard_points_idx = []
            discard_points_input = input(">> ").strip()
            if discard_points_input.lower() == "a":
                discard_points_idx = [i for i in range(len(points))]
            else:
                try: 
                    discard_points_idx = [int(idx) for idx in discard_points_input.split() if (0 <= int(idx) and int(idx) < len(points))]
                except ValueError:
                    raise CommandError("Input a valid index")

            # generate new points
            all_generated_points = []
            while(True):
                print("Generate additional points? (y/n)")
                generate_points_input = input(">> ").lower()
                generate_points = True if generate_points_input == "y" else False
                if not generate_points: break
                
                negative_points = []
                text_per_page = read_pdf(report.url)
                for text in text_per_page:
                    analysis = analyze(text)
                    if not analysis:
                        continue
                    if "negative thoughts" in analysis:
                        for neg_point in analysis["negative thoughts"]:
                            negative_points.append(neg_point)
                all_generated_points += negative_points

                # display new points
                print("Generated points: ")
                for (idx, point) in enumerate(all_generated_points):
                    print(f"{idx}: {point}")
            
            # select new points index to keep
            add_points_idx = []
            print("Select new point numbers to save. Type 'a' for all points.")
            add_points_input = input(">> ")
            if add_points_input.lower() == "a":
                add_points_idx = [i for i in range(len(all_generated_points))]
            else:
                try:
                    add_points_idx = [int(idx) for idx in add_points_input.split() if 0 <= int(idx) and int(idx) < len(all_generated_points)]
                except ValueError:
                    raise CommandError("Input a valid index")
            
            # delete points to discard, add points to add
            print("  These points will be DELETED:")
            for idx in discard_points_idx:
                print(f"    {idx}: {points[idx].content}")

            print("  These points will be ADDED:")
            for idx in add_points_idx:
                print(f"    {idx}: {all_generated_points[idx]}")

            print("Proceed the transaction? (y/n)")
            proceed = input(">> ").strip().lower()
            if proceed != "y":
                print("No changes made")
                return 1
            
            for idx in discard_points_idx:
                try: 
                    points[idx].delete()
                except Exception as e:
                    print(f"Deletion failed on point {idx}. Error: {e}")
            
            for idx in add_points_idx:
                try:
                    Point.objects.get_or_create(report=report, is_positive=False, content=all_generated_points[idx])
                except Exception as e:
                    print(f"Creation failed on point {idx}. Error: {e}")
            
            print("Done")
            return 0

        elif revise_target == "analyst":
            pass